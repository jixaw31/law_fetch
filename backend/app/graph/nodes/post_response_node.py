from uuid import uuid4
# from langchain_core.documents import Document
from qdrant_client.models import SparseVector, PointStruct

import asyncio
from langchain_core.messages import HumanMessage, AIMessage
from dotenv import load_dotenv
load_dotenv()

from app.container import container
from app.utils.my_utils import dynamic_split


async def post_response_node(state):
    last_human_message = [m for m in state['messages'] if m.type=="human"][-1]

    ai_res = [m for m in state['messages'] if m.type=="ai"][-1]
    print("Messages Types: ", last_human_message.type, ai_res.type)
    
    # Creating an embedding out of the last interaction.
    interaction_content = "\nHuman: " + last_human_message.content + "\nAI: " + ai_res.content
    
    # Initialize status trackers
    postgres_status = "NOT_ATTEMPTED"
    qdrant_status = "NOT_ATTEMPTED"
    neo4j_status = "NOT_ATTEMPTED"
    # INSERTING INTERACTION TO POSTGRES=================================================================
    try:
        deduplicator = container.deduplicator()

        # NOTE Insert with duplicate prevention partial precision
        # inserted, msg_id = await deduplicator.insert_without_duplicate
        
        inserted_exact, interaction_id = await deduplicator.insert_exact_only(
            content=interaction_content,
            id=ai_res.id,
            timestamp=ai_res.response_metadata['timestamp'],
            user_id=state['collection_name'] 
        )
        
        if inserted_exact:
            print(f"✅ Interaction inserted with ID: {interaction_id}")
            postgres_status = "OK"
        else:
            print("⚠️ Duplicate detected - message not inserted")
            postgres_status = "DUPLICATE"
            
    except KeyError as e:
        print(f"❌ PostgreSQL KeyError - missing field: {e}")
        postgres_status = f"FAILED: Missing field {e}"
        
    except Exception as e:
        print(f"❌ PostgreSQL insertion failed: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        postgres_status = f"FAILED: {str(e)}"
    
    # INSERTING CHUNKS OF INTERACTION TO QDRANT=================================================================
    try:
        interaction_chunks = dynamic_split(interaction_content)
        
        # interaction_chunks_docs = [
        #     Document(
        #         page_content=chunk, 
        #         id=str(uuid4()), 
        #         metadata={"lc_run_id": ai_res.id}
        #     ) for chunk in interaction_chunks
        # ]
        
        # lc_qdrant_client = container.lc_qdrant_client(
        #     collection_name=state['collection_name'] 
        # )

        # ids = await lc_qdrant_client.aadd_documents(documents=interaction_chunks_docs)
        
        # print(f"✅ {len(ids)} vectors added to collection '{state['collection_name'] }'")
        
        embedding_model = container.embedding_model()
        sparse_embedder = container.async_app.sparse_embedding_client()
        qdrant_client = container.qdrant_client()

        dense_vectors = await embedding_model.aembed_documents(interaction_chunks)
        try:
            sparse_vectors = await sparse_embedder.embed_documents(interaction_chunks)
        finally:
            await sparse_embedder.close()

        

        points_to_add = [
            PointStruct(
                id=str(uuid4()), 
                payload={
                    "page_content": interaction_chunks[i],
                    "metadata":{
                    "lc_run_id":ai_res.id
                    }
                }, 
                vector={
                    "dense": dense_vectors[i], 
                    "sparse": SparseVector(
                        indices=sparse_vectors["embeddings"][i]['indices'], 
                        values=sparse_vectors["embeddings"][i]['values']
                    )
                }
            ) for i in range(len(interaction_chunks))
        ]
        
        
        await qdrant_client.upsert(
            collection_name=state['collection_name'],
            points=points_to_add
        )
        
        
        qdrant_status = f"OK: {len(interaction_chunks)} vectors"
        
    except Exception as e:
        print(f"❌ Qdrant insertion failed: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        qdrant_status = f"FAILED: {str(e)}"

    # EXTRACTING & INSERTING NODES AND RELATIONS INTO NEO4J=================================================================

    # try:
    #     graph_extractor_instance = container.graph_extractor()
    #     async with graph_extractor_instance as extractor:
    #         # Process the actual interaction content with chunk tracking
    #         # Pass the interaction ID as document_id for grouping
    #         result = await extractor.process_document(
    #             text=interaction_content,
    #             document_id=ai_res.id,
    #             chunk_id=ai_res.id,  # Use interaction_id as the source identifier
    #         )
            
    #         print(f"✅ Neo4j extraction complete:")
    #         print(f"   - {len(result.nodes)} nodes extracted")
    #         print(f"   - {len(result.relationships)} relationships extracted")
            
    #         # Verify source tracking was added
    #         for node_id, node_data in result.nodes.items():
    #             if "source_chunk_id" in node_data.get("properties", {}):
    #                 print(f"   ✓ Node {node_id} tracked to chunk: {node_data['properties']['source_chunk_id']}")
            
    #         neo4j_status = f"OK: {len(result.nodes)} nodes, {len(result.relationships)} rels"
            
    # except Exception as e:
    #     print(f"❌ Neo4j extraction/insertion failed: {type(e).__name__}: {e}")
    #     import traceback
    #     traceback.print_exc()
    #     neo4j_status = f"FAILED: {str(e)}"
    
    # Return status to state
    return {
        "postgres_save": postgres_status,
        "qdrant_save": qdrant_status,
        "neo4j_save": neo4j_status
    }

async def main():
    ai_res = AIMessage(content="Hi, What can I do for you?", id=str(uuid4()))
    ai_res.response_metadata['input_tokens'] = 200
    ai_res.response_metadata['completion_tokens'] = 250
    ai_res.response_metadata['timestamp'] = 25555
    await post_response_node(
        {
            "messages":[HumanMessage(content="Who was Richard Feynman? Give me a 250 words essay."), ai_res],
            "collection_name":"847f5e78-25b0-46b0-8188-1ebefd9c2772" # 
        },
    )

if __name__ == "__main__":
    asyncio.run(main())