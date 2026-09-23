import asyncio
from app.container import container

reranker_client = container.reranker_client()

tokenizer = container.tokenizer()



def deduplicate_points(points):
    seen = set()
    unique_points = []

    for point in points:
        if point.id in seen:
            continue

        seen.add(point.id)
        unique_points.append(point)

    return unique_points

async def reranker(state):
    print("NODE: RERANKER")
    

    MAX_QUERY_TOKENS = 256
    MAX_DOC_TOKENS = 700
    
    # TODO TODO TODO MUST CHECK WHAT DOES TRUNCATION FROM RIGHT MEANS HERE, WHAT IS THE OUTPUT.

    # LAWS =========================================================================
    laws_points = state["hybrid_points"]
    laws_documents = [
        p.payload["embedding_text"]
        for p in laws_points
    ]
    encoded = tokenizer.encode_batch(
        laws_documents,
        add_special_tokens=False,
    )
    for enc in encoded:
        if len(enc.ids) > MAX_DOC_TOKENS:
            enc.truncate(MAX_DOC_TOKENS)
    laws_documents = tokenizer.decode_batch(
        [enc.ids for enc in encoded],
        skip_special_tokens=True,
    )
    # LAW_QA ========================================================================
    law_QA_points = state['law_QA_points']
    law_QA_documents = [
        p.payload["question"]
        for p in law_QA_points
    ]
    encoded = tokenizer.encode_batch(
        law_QA_documents,
        add_special_tokens=False,
    )
    for enc in encoded:
        if len(enc.ids) > MAX_DOC_TOKENS:
            enc.truncate(MAX_DOC_TOKENS)
    law_QA_documents = tokenizer.decode_batch(
        [enc.ids for enc in encoded],
        skip_special_tokens=True,
    )
    # QUERY ==========================================================================
    query = state["enhanced_queries"]["dense"]
    query_encoded = tokenizer.encode(
        query,
        add_special_tokens=False,
    )
    query_encoded.truncate(MAX_QUERY_TOKENS)
    query = tokenizer.decode(
        query_encoded.ids,
        skip_special_tokens=True,
    )

    formatted_query = (
        "Instruct: Rank the documents based on their relevance to the given query.\n"
        f"Query: {query}"
    )

    # Paylaod for reranker model api request
    laws_payload = {
        "model": "qwen3-reranker-0.6b",
        "query": formatted_query,
        "documents": laws_documents,
        "top_n": len(laws_documents),
    }
    laws_response = await reranker_client._client.post(
        "/rerank",
        json=laws_payload,
    )
    print("STATUS:", laws_response.status_code)
    laws_response.raise_for_status()
    laws_results = laws_response.json()

    # Paylaod for reranker model api request
    QA_payload = {
        "model": "qwen3-reranker-0.6b",
        "query": formatted_query,
        "documents": law_QA_documents,
        "top_n": len(law_QA_documents),
    }
    QA_response = await reranker_client._client.post(
        "/rerank",
        json=QA_payload,
    )
    print("STATUS:", QA_response.status_code)
    QA_response.raise_for_status()
    QA_results = QA_response.json()


    laws_reranked_points = []
    for item in laws_results["results"]:
        
        idx = item["index"]
        score = item["relevance_score"]

        point = laws_points[idx]

        # if score > 0.9:
        point.payload["reranker_score"] = score
        laws_reranked_points.append(point)

    law_QA_reranked_points = []
    for item in QA_results["results"]:
        
        idx = item["index"]
        score = item["relevance_score"]

        point = law_QA_points[idx]

        if score > 0.9:
            point.payload["reranker_score"] = score
            law_QA_reranked_points.append(point)
    
    # for p in law_QA_reranked_points:
    #     print("reranked score: \n", p.payload["reranker_score"])
    # print("========================================")
    # for p in laws_reranked_points:
    #     print("reranked score: \n", p.payload["reranker_score"])
    
    # import sys;sys.exit()
    # laws_reranked_points.sort(
    #     key=lambda p: p.score,
    #     reverse=True
    # )

    # law_QA_reranked_points.sort(
    #     key=lambda p: p.score,
    #     reverse=True
    # )
    # for p in laws_reranked_points:
    #     print("embedding score:", p.score)
    #     print("reranker score", p.payload["reranker_score"])
    #     print("embedding_text", p.payload['embedding_text'])
    #     print("======================================================================")
    
    # import sys;sys.exit()
    return {"reranked_points": {
        "laws_reranked_points": laws_reranked_points, 
        # "law_QA_reranked_points": law_QA_reranked_points
        }
    }

if __name__ == "__main__":
    asyncio.run(reranker())