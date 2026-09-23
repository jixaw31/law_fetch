import requests
from typing import List

import aiohttp
from aiohttp import ClientTimeout

# Server configuration
BASE_URL = "http://localhost:8015"

class SparseEmbeddingClient:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
    
    def health_check(self) -> dict:
        """Check if server is healthy"""
        response = requests.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    def query_embed(self, text: str) -> dict:
        """Get sparse embedding for a single query"""
        response = requests.post(
            f"{self.base_url}/query_embed",
            json={"text": text}
        )
        response.raise_for_status()
        return response.json()
    
    def embed_documents(self, documents: List[str], batch_size: int = 32) -> dict:
        """Get sparse embeddings for multiple documents"""
        response = requests.post(
            f"{self.base_url}/embed",
            json={"documents": documents, "batch_size": batch_size}
        )
        response.raise_for_status()
        return response.json()
    
    def get_model_info(self) -> dict:
        """Get model information"""
        response = requests.get(f"{self.base_url}/info")
        response.raise_for_status()
        return response.json()

class AsyncSparseEmbeddingClient:
    def __init__(self, base_url: str = BASE_URL, timeout: int = 30):
        self.base_url = base_url
        self.timeout = ClientTimeout(total=timeout)
        self._session: aiohttp.ClientSession | None = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create a reusable session"""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(timeout=self.timeout)
        return self._session
    
    async def close(self):
        """Close the session properly"""
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def __aenter__(self):
        """Context manager entry"""
        await self._get_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        await self.close()
    
    async def health_check(self) -> dict:
        """Check if server is healthy (async)"""
        session = await self._get_session()
        async with session.get(f"{self.base_url}/health") as response:
            response.raise_for_status()
            return await response.json()
    
    async def query_embed(self, text: str) -> dict:
        """Get sparse embedding for a single query (async)"""
        session = await self._get_session()
        async with session.post(
            f"{self.base_url}/query_embed",
            json={"text": text}
        ) as response:
            response.raise_for_status()
            return await response.json()
    
    async def embed_documents(self, documents: List[str], batch_size: int = 32) -> dict:
        """Get sparse embeddings for multiple documents (async)"""
        session = await self._get_session()
        
        # Calculate dynamic timeout based on batch size
        # Assume 2 seconds per document for SPLADE
        estimated_time = batch_size * 2 + 10  # 10 seconds overhead
        timeout = max(30, estimated_time)  # At least 30 seconds
        
        async with session.post(
            f"{self.base_url}/embed",
            json={"documents": documents, "batch_size": batch_size},
            timeout=ClientTimeout(total=timeout)  # Override timeout for this request
        ) as response:
            response.raise_for_status()
            return await response.json()
    
    async def get_model_info(self) -> dict:
        """Get model information (async)"""
        session = await self._get_session()
        async with session.get(f"{self.base_url}/info") as response:
            response.raise_for_status()
            return await response.json()
        

# # Example usage
# if __name__ == "__main__":
#     client = SparseEmbeddingClient()
    
#     # 1. Health check
#     print("=" * 50)
#     print("1. Health Check:")
#     print(client.health_check())
    
#     # 2. Query embedding (single text)
#     print("\n" + "=" * 50)
#     print("2. Query Embedding:")
#     result = client.query_embed("hello there")
#     print(f"Indices: {result['indices'][:10]}...")  # First 10 indices
#     print(f"Values: {result['values'][:10]}...")    # First 10 values
#     print(f"Total non-zero elements: {len(result['indices'])}")
    
#     # 3. Document embeddings (multiple documents)
#     print("\n" + "=" * 50)
#     print("3. Document Embeddings:")
#     documents = ["hello there", "how ye doing?", "this is a test document"]
#     results = client.embed_documents(documents, batch_size=2)
    
#     for i, embedding in enumerate(results['embeddings']):
#         print(f"\nDocument {i+1}: '{documents[i]}'")
#         print(f"  Non-zero elements: {len(embedding['indices'])}")
#         print(f"  First 5 indices: {embedding['indices'][:5]}")
#         print(f"  First 5 values: {embedding['values'][:5]}")
    
#     # 4. Model info
#     print("\n" + "=" * 50)
#     print("4. Model Info:")
#     print(client.get_model_info())

async def main():
    async_client = AsyncSparseEmbeddingClient()
    
    try:
        # 1. Health check
        print("=" * 50)
        print("1. Health Check:")
        health = await async_client.health_check()
        print(health)
        
        # 2. Query embedding (single text)
        print("\n" + "=" * 50)
        print("2. Query Embedding:")
        result = await async_client.query_embed("hello there")
        print(f"Indices: {result['indices'][:10]}...")  # First 10 indices
        print(f"Values: {result['values'][:10]}...")    # First 10 values
        print(f"Total non-zero elements: {len(result['indices'])}")
        
        # 3. Document embeddings (multiple documents)
        print("\n" + "=" * 50)
        print("3. Document Embeddings:")
        documents = ["hello there", "how ye doing?", "this is a test document"]
        results = await async_client.embed_documents(documents, batch_size=2)
        
        for i, embedding in enumerate(results['embeddings']):
            print(f"\nDocument {i+1}: '{documents[i]}'")
            print(f"  Non-zero elements: {len(embedding['indices'])}")
            print(f"  First 5 indices: {embedding['indices'][:5]}")
            print(f"  First 5 values: {embedding['values'][:5]}")
        
        # 4. Model info
        print("\n" + "=" * 50)
        print("4. Model Info:")
        info = await async_client.get_model_info()
        print(info)
        
    finally:
        await async_client.close()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
