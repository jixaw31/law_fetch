import asyncio
from app.container import container
from qdrant_client.models import SparseVector, Prefetch, Fusion, FusionQuery, Document


qdrant_client = container.qdrant_client()

embedding_model = container.embedding_model()

# async_app.sparse_embedding_client = container.async_app.sparse_embedding_client()

def min_max_normalize(points):
    scores = [p.score for p in points]

    min_score = min(scores)
    max_score = max(scores)

    if max_score == min_score:
        for p in points:
            p.score = 1.0
        return points

    for p in points:
        p.score = (p.score - min_score) / (max_score - min_score)

    return points

async def search(state):
    print("NODE: SEARCH")

    COLLECTION_NAME = "laws_1"

    dense_query_embedding = embedding_model.embed_query(state['enhanced_queries']['dense'])
    sparse_query = state['enhanced_queries']['sparse']
     

    laws_bm25_scored_points = await qdrant_client.query_points(
        collection_name="laws_1",
        query=Document(
            text=sparse_query,
            model="qdrant/bm25",
        ),
        using="bm25",
        limit=5,
        with_payload=True,
    )

    laws_dense_scored_points = await qdrant_client.query_points(
        collection_name=COLLECTION_NAME,
        using= "dense",
        query=dense_query_embedding,
        limit=5,
        with_payload=True,
    )

    hybrid_results = await qdrant_client.query_points(
        collection_name=COLLECTION_NAME,
        prefetch=[
            Prefetch(
                query=Document(
                    text=sparse_query,
                    model="qdrant/bm25",
                ),
                using="bm25",
                limit=20,
            ),
            Prefetch(
                query=dense_query_embedding,
                using="dense",
                limit=20,
            ),
        ],
        query=FusionQuery(fusion=Fusion.RRF),
        limit=10,
        with_payload=True,
    )
    

    # ============================================================================
    law_QA_dense_scored_points = await qdrant_client.query_points( 
        collection_name="law_QA",
        query=dense_query_embedding,
        limit=5,
        with_payload=True,
    )
    
    bm25_points = min_max_normalize(
        laws_bm25_scored_points.points
    )

    dense_points = min_max_normalize(
        laws_dense_scored_points.points
    )

    laws_points = bm25_points + dense_points
    laws_points = []
    laws_points.sort(
        key=lambda p: p.score,
        reverse=True
    )
    print([p.score for p in laws_points])
    
    law_QA_points = law_QA_dense_scored_points.points
    
    return {
        "laws_points": laws_points, 
        "law_QA_points": law_QA_points, 
        "hybrid_points": hybrid_results.points,
    }




if __name__ == "__main__":
    asyncio.run(search())