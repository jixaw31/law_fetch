import asyncio
from langchain.embeddings import init_embeddings
from typing import List
import pandas as pd
from tqdm import tqdm
from uuid import uuid4
import gc

def dynamic_batch_texts(list_of_dicts, tokenizer, max_length: int = 65530) -> List[List[str]]:
    """
    Dynamically batch texts based on token length limits.
    
    Args:
        texts: List of input strings
        tokenizer_path: Path to tokenizer.json file
        max_length: Maximum token length per batch (default: 8192)
    
    Returns:
        List of batches, where each batch is a list of strings
    """
    
    questions = [x['questionBody'] for x in list_of_dicts]
    answers_s = [x['answers'] for x in list_of_dicts]
    encodings = tokenizer.encode_batch(questions)
    text_lengths = [(question, len(enc.ids), answers) for question, enc, answers in zip(questions, encodings, answers_s)]

    # Sort by length (longest first) for better packing
    text_lengths.sort(key=lambda x: x[1], reverse=True)

    # Create batches
    batches = []
    current_batch = []
    current_token_count = 0

    for question, length, answers in text_lengths:
        # If a single text exceeds max_length, handle it separately
        if length > max_length:
            # If we have accumulated texts, save the current batch first
            if current_batch:
                batches.append(current_batch)
                current_batch = []
                current_token_count = 0
            
            # Put the long text in its own batch (truncation will happen later)
            batches.append([(question, answers)])
            continue
        
        # If adding this text exceeds limit, start new batch
        if current_batch and current_token_count + length > max_length:
            batches.append(current_batch)
            current_batch = [(question, answers)]
            current_token_count = length
        else:
            current_batch.append((question, answers))
            current_token_count += length

    # Add final batch
    if current_batch:
        batches.append(current_batch)

    return batches

embedding_model = init_embeddings(
    model="openai:qwen3_0.6B_gguf",
    # model_provider="openai",
    api_key="not-needed",
    base_url="http://0.0.0.0:8080/v1",
    check_embedding_ctx_length=False,
)
# insertion into qdrant
from qdrant_client import AsyncQdrantClient, models

qdrant_client = AsyncQdrantClient(   
    host="localhost",
    port=6333,
    https=False,
    api_key="123456789",
    check_compatibility=False,
)
from tokenizers import Tokenizer

# Load a pre-trained tokenizer from the hub
tokenizer = Tokenizer.from_file("qwen_tokenizer/tokenizer.json")


async def main():
    

    input_path = '/home/jixaw/law_datasets/Perset_QA/train_5.jsonl'
    source = "_".join(input_path.split("/")[-2:])
    print(source)
    
    # Method 1: Use pandas directly (recommended)
    df = pd.read_json(input_path, lines=True)
    list_of_dicts = df.to_dict('records')

    batches = dynamic_batch_texts(list_of_dicts, tokenizer)

    
    # creating the collection
    COLLECTION_NAME = "law_QA"
    res = await qdrant_client.collection_exists(COLLECTION_NAME)
    if not res:
        await qdrant_client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=models.VectorParams(
                size=1024,
                distance=models.Distance.COSINE
            )
        )

    

    for i, batch in tqdm(enumerate(batches)):
        
        questions_to_vectorize = [x[0] for x in batch]
        embeddings = embedding_model.embed_documents(questions_to_vectorize)
        
        points = []
        for j, emb in enumerate(embeddings):
            p = models.PointStruct(
                id = str(uuid4()),
                vector=emb,
                payload={
                    "question": batches[i][j][0],
                    "source": source,
                    "answers": batches[i][j][1],
                    "status": "not specified",
                })
            points.append(p)
        await qdrant_client.upsert(
            collection_name="law_QA",
            points=points
        )

        # Clear memory
        del embeddings
        del points
        gc.collect()


if __name__ == "__main__":
    asyncio.run(main())