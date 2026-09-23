import asyncio
from dynamic_batch_texts import dynamic_batch_texts
from qdrant_client import models
import json
from uuid import uuid4
from app.container import container
from qdrant_client.http.exceptions import UnexpectedResponse
from glob import glob
import gc
from tqdm import tqdm


tokenizer = container.tokenizer()

qdrant_client = container.qdrant_client()

embedding_model = container.embedding_model()

async_app.sparse_embedding_client = container.async_app.sparse_embedding_client()



async def fill_qdrant(collection_name: str):
    print("COLLECTION_NAME: ", collection_name)

    
    for file_path in glob("laws_data/*.json"):
        
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        batches = dynamic_batch_texts(data, tokenizer, 65000)

        
        for batch in tqdm(batches):
        
            texts_to_vectorize = [x["embedding_text"] for x in batch]
            embeddings = embedding_model.embed_documents(texts_to_vectorize)
            try:
                sparse_embeddings = await async_app.sparse_embedding_client.embed_documents(texts_to_vectorize, batch_size=32)
            except Exception as e:
                # Print the full error with traceback
                print(f"ERROR: {e}")
                print(f"Error type: {type(e)}")
                import traceback
                traceback.print_exc()  # This prints the full stack trace
            finally:
                await async_app.sparse_embedding_client.close()

            points = []
            for j, emb in enumerate(embeddings):
                p = models.PointStruct(
                    id = str(uuid4()),
                    vector={"dense": emb, "sparse": sparse_embeddings["embeddings"][j]},
                    payload=batch[j],
                )
                points.append(p)
            
            await qdrant_client.upsert(
                collection_name="laws",
                points=points
            )

            del sparse_embeddings
            del embeddings
            del points
            gc.collect()
            print(f"{file_path} DONE.")
    


COLLECTION_NAME = "laws"

if __name__ == "__main__":
    asyncio.run(fill_qdrant(COLLECTION_NAME))