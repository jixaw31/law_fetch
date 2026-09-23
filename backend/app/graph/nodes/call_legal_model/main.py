from ...schemas import MyMessagesState
from app.container import container
from qdrant_client.models import Filter, FieldCondition, MatchValue
from .sys_message import get_sys_message
from app.utils.my_utils import count_tokens
from langgraph.graph import MessagesState
import asyncio
from langchain_core.messages import RemoveMessage, HumanMessage

embedding_model = container.embedding_model()
qdrant_client = container.qdrant_client()
gemma3 = container.qwen_35()


tokenizer = container.tokenizer()

async def call_legal_model(state):

    print("NODE: call_legal_model")

    print(state['messages'])
    # import sys;sys.exit()

    laws_reranked_points = state["reranked_points"]["laws_reranked_points"]
    # law_QA_reranked_points = state["reranked_points"]["law_QA_reranked_points"]
    
    context_parts = []

    if len(state["reranked_points"]) == 0:
        print("NO MATCH FOUND")
        context = "EMPTY"
    else:

        for i, point in enumerate(laws_reranked_points[:5], 1):
            payload = point.payload

            context_parts.append(
                f"""[Source {i}]
        Law: {payload.get("law_title")}
        Book: {payload.get("book")}
        Chapter: {payload.get("chapter")}
        Section: {payload.get("section")}
        Subsection: {payload.get("subsection")}
        Article: {payload.get("article_number")}
        Status: {payload.get("article_status")}

        Text:
        {payload.get("content")}
        """
            )
        # for i, point in enumerate(law_QA_reranked_points[:3], 1):
        #     payload = point.payload
        #     context_parts.append(f"Question: {payload.get("question")}\n\n")
        #     for ans in payload.get("answers")[:3]:
        #         context_parts.append(f"Answer: {ans}\n")
                
            

        context = "\n\n".join(context_parts)
    
    
    
    sys_message = get_sys_message(context)
    llm_input = [sys_message] + state['messages']
    
    print(llm_input)
    # import sys;sys.exit()
    # INPUT CONTROL=================================================================================
    n_input_tokens = count_tokens(llm_input, tokenizer)

    print("n_input_tokens", n_input_tokens)
    # import sys;sys.exit()
    MAX_INPUT_TOKENS = 4096
    if n_input_tokens > MAX_INPUT_TOKENS:
        i = 0

        while MAX_INPUT_TOKENS < n_input_tokens:
            if llm_input[i].type == "system":
                pass
            else:
                n_input_tokens -= len(tokenizer.encode(state['messages'][i].content))
                print("last deleted message tokens", len(tokenizer.encode(state['messages'][i].content)))
                print("last deleted message type", state['messages'][i].type)
                state['messages'].append(RemoveMessage(state['messages'][i].id))
                print("n_input_tokens", n_input_tokens)
                print(f"message with id: {state['messages'][i].id} removed.")
            i += 1


    res = await gemma3.ainvoke(llm_input)

    print("RES DOT CONTENT")
    print(res.content)

    
    return {"messages": [res], "retrieved_content": context}


if __name__ == "__main__":
    asyncio.run(call_legal_model({"messages": [get_sys_message(""), HumanMessage(content="hello there!")]}))
    
