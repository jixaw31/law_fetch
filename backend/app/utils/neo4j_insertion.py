import json
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from neo4j import GraphDatabase, AsyncGraphDatabase, AsyncDriver
from pydantic import BaseModel, Field
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

# ============ Pydantic Models for Structured Output ============

class Relationship(BaseModel):
    """Represents a relationship between two nodes"""
    source: str
    source_label: str
    target: str
    target_label: str
    relationship_type: str
    properties: Dict[str, Any] = Field(default_factory=dict)

class ExtractionResult(BaseModel):
    """Complete extraction result from a text chunk"""
    nodes: Dict[str, Dict[str, Any]] = Field(default_factory=dict)  # node_id -> {label, properties}
    relationships: List[Relationship] = Field(default_factory=list)



class GraphExtractor:
    """
    Manual LLM-based entity and relationship extractor for Neo4j.
    Handles chunking, LLM extraction, and Neo4j insertion.
    """
    
    def __init__(
        self,
        llm: AsyncOpenAI,
        model_name: str, 
        neo4j_uri: str,
        neo4j_user: str,
        neo4j_password: str,
        chunk_size: int = 2000,
        chunk_overlap: int = 200,
    ):
        self.llm = llm
        self.model_name = model_name
        self.driver: AsyncDriver
        self.neo4j_uri = neo4j_uri
        self.neo4j_user = neo4j_user
        self.neo4j_password = neo4j_password
        
        # Schema constraints (optional but recommended)
        

        # ✅ CORRECT - define variables first
        entities = ["PERSON", "ORGANIZATION", "LOCATION", "PROJECT", "TECHNOLOGY"]
        relations = ["WORKS_FOR", "LOCATED_IN", "COLLABORATES_ON", "MENTORS", "USES", "MANAGES"]
        potential_schema = [
            ("PERSON", "WORKS_FOR", "ORGANIZATION"),
            ("PERSON", "LOCATED_IN", "LOCATION"),
            ("PERSON", "COLLABORATES_ON", "PROJECT"),
            ("PERSON", "MENTORS", "PERSON"),
            ("PROJECT", "USES", "TECHNOLOGY"),
            ("ORGANIZATION", "MANAGES", "PROJECT"),
        ]
        
        self.entities = entities 
        self.relations = relations 
        self.potential_schema = potential_schema 
        
        # Text processing
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
    async def __aenter__(self):
        """Connect to Neo4j on context entry"""
        self.driver = AsyncGraphDatabase.driver(
            self.neo4j_uri,
            auth=(self.neo4j_user, self.neo4j_password)
        )
        await self.driver.verify_connectivity()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Close Neo4j connection on context exit"""
        if self.driver:
            await self.driver.close()
    
    def _chunk_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks"""
        chunks = []
        start = 0
        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            chunk = text[start:end]
            chunks.append(chunk)
            start += (self.chunk_size - self.chunk_overlap)
        return chunks
    
    def _build_extraction_prompt(self, chunk: str) -> str:
        """Build the prompt for LLM extraction with schema constraints"""
        schema_instruction = ""
        if self.potential_schema:
            schema_instruction = f"""
            VALID RELATIONSHIP PATTERNS (only extract these):
            {json.dumps(self.potential_schema, indent=2)}
            """
        
        return f"""
        Extract all entities (nodes) and relationships from the following text.
        
        ALLOWED ENTITY TYPES: {', '.join(self.entities)}
        ALLOWED RELATIONSHIP TYPES: {', '.join(self.relations)}
        {schema_instruction}
        
        Rules:
        1. ONLY extract entity types from the allowed list above
        2. ONLY extract relationship types from the allowed list above
        3. Each entity must have a unique ID (use name or generate one)
        4. Include relevant properties for each entity (e.g., role, location, date)
        5. If you're unsure about an entity type, leave it out
        6. DO NOT extract relationships that don't match the allowed patterns
        
        Text to analyze:
        {chunk}
        
        Return JSON with this structure:
        {{
            "nodes": {{
                "unique_node_id_1": {{
                    "label": "PERSON",
                    "properties": {{"name": "Alice", "role": "Data Scientist"}}
                }},
                "unique_node_id_2": {{
                    "label": "ORGANIZATION", 
                    "properties": {{"name": "TechCorp", "location": "Seattle"}}
                }}
            }},
            "relationships": [
                {{
                    "source": "unique_node_id_1",
                    "source_label": "PERSON",
                    "target": "unique_node_id_2",
                    "target_label": "ORGANIZATION",
                    "relationship_type": "WORKS_FOR",
                    "properties": {{"since": "2020"}}
                }}
            ]
        }}
        """
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def _extract_from_chunk(self, chunk: str, chunk_id: Optional[str] = None) -> ExtractionResult:
        """Extract nodes and relationships from a single text chunk using LLM"""
        
        prompt = self._build_extraction_prompt(chunk)
        
        response = await self.llm.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": "You are a precise knowledge graph extractor. Extract entities and relationships exactly as specified in the schema. Always respond with valid JSON only. Do not use markdown formatting."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=2048,
        )
        
        content = response.choices[0].message.content
        
        # Clean markdown if present
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        elif content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()
        
        result_json = json.loads(content)
        
        # ADD SOURCE TRACKING TO NODES
        nodes = result_json.get("nodes", {})
        if chunk_id:
            for node_id, node_data in nodes.items():
                if "properties" not in node_data:
                    node_data["properties"] = {}
                node_data["properties"]["source_chunk_id"] = chunk_id
                
        
        return ExtractionResult(
            nodes=nodes,
            relationships=[Relationship(**rel) for rel in result_json.get("relationships", [])]
        )
    
    async def _merge_nodes(self, nodes: Dict[str, Dict[str, Any]]):
        """Merge nodes into Neo4j using MERGE to avoid duplicates"""
        async with self.driver.session() as session:
            for node_id, node_data in nodes.items():
                label = node_data.get("label")
                properties = node_data.get("properties", {})
                
                # Create properties map with the node_id as the unique identifier
                properties["extraction_id"] = node_id
                
                # Use MERGE to avoid duplicates (assuming 'name' or 'id' is unique)
                # You can adjust the uniqueness constraint based on your data
                merge_query = f"""
                MERGE (n:{label} {{name: $name}})
                SET n += $properties
                RETURN n
                """
                
                await session.run(
                    merge_query,
                    name=properties.get("name", node_id),
                    properties=properties
                )
    
    async def _create_relationships(self, relationships: List[Relationship]):
        """Create relationships between existing nodes"""
        async with self.driver.session() as session:
            for rel in relationships:
                query = f"""
                MATCH (source:{rel.source_label} {{name: $source_name}})
                MATCH (target:{rel.target_label} {{name: $target_name}})
                MERGE (source)-[r:{rel.relationship_type}]->(target)
                SET r += $properties
                RETURN r
                """
                
                await session.run(
                    query,
                    source_name=rel.source,
                    target_name=rel.target,
                    properties=rel.properties
                )
    
    async def process_document(
        self, 
        text: str, 
        document_id: str,
        chunk_id: str  # ← ADD THIS PARAMETER
    ) -> ExtractionResult:
        """
        Main entry point: process a document through extraction and insertion.
        
        Args:
            text: The raw text to process
            document_id: Optional ID for the source document
            chunk_id: Optional ID for the source chunk (for tracking)
            
        Returns:
            ExtractionResult with all extracted nodes and relationships
        """
        if not self.driver:
            raise RuntimeError("Not connected to Neo4j. Use 'async with' context manager.")
        
        print(f"📄 Processing document of {len(text)} characters...")
        
        # 1. Chunk the text
        chunks = self._chunk_text(text)
        print(f"✂️ Split into {len(chunks)} chunks")
        
        # 2. Extract from each chunk
        all_nodes = {}
        all_relationships = []
        
        for i, chunk in enumerate(chunks):
            # Create chunk-specific ID if not provided
            current_chunk_id = chunk_id
            
            print(f"  🔍 Processing chunk {i+1}/{len(chunks)}...")
            try:
                # PASS CHUNK_ID TO EXTRACTION METHOD
                result = await self._extract_from_chunk(chunk, chunk_id=current_chunk_id)
                all_nodes.update(result.nodes)
                all_relationships.extend(result.relationships)
                print(f"    ✓ Found {len(result.nodes)} nodes and {len(result.relationships)} relationships")
            except Exception as e:
                print(f"    ❌ Failed: {e}")
                continue
        
        print(f"\n📊 Extraction summary:")
        print(f"   - Total unique nodes: {len(all_nodes)}")
        print(f"   - Total relationships: {len(all_relationships)}")
        
        # 3. Insert into Neo4j
        print(f"\n💾 Inserting into Neo4j...")
        await self._merge_nodes(all_nodes)
        print(f"   ✓ Inserted {len(all_nodes)} nodes")
        
        await self._create_relationships(all_relationships)
        print(f"   ✓ Created {len(all_relationships)} relationships")
        
        # 4. Return results
        return ExtractionResult(nodes=all_nodes, relationships=all_relationships)


# ============ Usage Example ============

async def main():
    # Initialize clients
    async_openai_client = AsyncOpenAI(
        api_key="not-needed",
        base_url="http://localhost:8007/v1",
        max_retries=2,
        timeout=60.0,
    )
    
    # Create and use the extractor
    async with GraphExtractor(
        llm=async_openai_client,
        neo4j_uri="bolt://localhost:7687",
        neo4j_user="neo4j",
        model_name="qwen3_4b_4bit",
        neo4j_password="2281249271",
    ) as extractor:
        
        # Process a document
        document = """
        Alice Johnson works as a Senior Data Scientist at TechCorp in Seattle. 
        She is currently leading the "Project Atlas" which uses Python and Kubernetes.
        Bob Williams collaborates with Alice on Project Atlas. 
        Bob is also being mentored by Alice.
        TechCorp's headquarters is located in Seattle and manages multiple AI projects.
        """
        
        result = await extractor.process_document(document)
        
        print(f"\n✅ Done! Final extraction:")
        for node_id, node_data in result.nodes.items():
            print(f"  Node {node_id}: {node_data}")
        for rel in result.relationships:
            print(f"  Relationship: {rel.source} -[{rel.relationship_type}]-> {rel.target}")

# Run
if __name__ == "__main__":
    asyncio.run(main())