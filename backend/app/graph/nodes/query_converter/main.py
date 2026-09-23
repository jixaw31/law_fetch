from langchain_core.messages import HumanMessage, SystemMessage
import json
from app.container import container
from pydantic import BaseModel, Field

class EnhancedQuery(BaseModel):
    dense_query: str = Field(
        description="The rewritten, optimized search query with corrected spelling"
    )
    sparse_query: str = Field(
        description="A list of key terms and important keywords extracted from the original user's raw query, separated by spaces"
    )

llm = container.qwen_35()

async def convert_query(state)-> EnhancedQuery:
    
    # LAST HUMAN MESSAGE
    last_human_message = [m for m in state['messages'] if m.type == "human"][-1]
    messages = [
        SystemMessage(
            content="""You are an expert query rewriter for a search engine.

Your task is to convert the user's raw question into optimized search queries.

Follow these rules:
1. For the dense query: Fix only spelling, grammar, and punctuation errors. Do not paraphrase, rephrase, clarify, or change the wording beyond what is necessary to correct errors.
2. For the sparse query: Extract space-separated keywords from the original query.

Output a valid JSON object with two keys:
- "dense_query": The corrected version of the original query (errors fixed, but otherwise identical).
- "sparse_query": Space-separated keywords from the original query."""
        ), 
        HumanMessage(content=last_human_message.content)
    ]

    llm_with_structured_output = llm.with_structured_output(EnhancedQuery)

    # 6. Use it
    result = await llm_with_structured_output.ainvoke(messages, config=None)
    print(result)
    
    return {"enhanced_queries": {"dense": result.dense_query, "sparse": result.sparse_query}}


async def main():
    res = await convert_query({"messages": [HumanMessage("Give me a 250 words essay about Einstein")]})
    print(res)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())