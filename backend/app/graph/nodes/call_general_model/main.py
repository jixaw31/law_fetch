from langchain_core.messages import HumanMessage, AIMessage, RemoveMessage, AnyMessage
import asyncio, numpy as np
from langchain_core.messages import AnyMessage
# from langchain_core.documents import Document
from datetime import datetime
# from qdrant_client.models import Prefetch, SumExpression, MultExpression, FormulaQuery

# from app.utils.get_interactions import get_interactions_batch
from app.utils.my_utils import count_tokens
# from app.utils.minmax_scaler import minmax_scale_with_range
from app.container import container
from .sys_message import general_system_message

qdrant_client = container.qdrant_client()

embedding_model = container.embedding_model()

# sparse_embedder = container.async_app.sparse_embedding_client()

llm = container.qwen_35()

tokenizer = container.tokenizer()


async def call_general_model(state):
    

    # =====CREATING A COPY OF THE CURRENT CONVERSATION'S MESSAGES============================================
    
    messages_list:list[AnyMessage] = []
    
    for m in state['messages']:
        if m.type == "ai":
            messages_list.append(AIMessage(content=m.content, id=m.id))
        elif m.type =="human":
            messages_list.append(HumanMessage(content=m.content, id=m.id))
        else:
            pass # for now
    
    system_message = general_system_message
    
    
    messages = [system_message] + messages_list
    print("MESSAGES", messages)
    # INPUT CONTROL=================================================================================
    n_input_tokens = count_tokens(messages, tokenizer)

    print("input tokens: ", n_input_tokens)
    MAX_INPUT_TOKENS = 4096 # can go up to 4096
    if n_input_tokens > MAX_INPUT_TOKENS:
        i = 0
        
        while MAX_INPUT_TOKENS < n_input_tokens:
            if state['messages'][i].type == "system":
                pass
            else:
                n_input_tokens -= len(tokenizer.encode(state['messages'][i].content))
                print("last deleted message tokens", len(tokenizer.encode(state['messages'][i].content)))
                print("last deleted message type", state['messages'][i].type)
                state['messages'].append(RemoveMessage(state['messages'][i].id))
                print("n_input_tokens", n_input_tokens)
                print(f"message with id: {state['messages'][i].id} removed.")
            i += 1 

    # =====THE LLM CALL==============================================================================
    ai_res = await llm.ainvoke(messages)
    print(ai_res.content)
    # ai_res = AIMessage(content="Hi, What can I do for you?", id=str(uuid4()))
    
    # we could move these guys to post_response_node as well.
    ai_res.response_metadata['input_tokens'] = n_input_tokens
    ai_res.response_metadata['completion_tokens'] = count_tokens([ai_res], tokenizer)
    ai_res.response_metadata['timestamp'] = datetime.now().timestamp()

    ai_res.additional_kwargs['node_name'] = "call_model"

    last_human_msg = [m for m in state['messages'] if m.type == "human"][-1]
    return {
        "messages": [ai_res],
        "truncated_messages":[last_human_msg, ai_res]
    }

if __name__ == "__main__":
    async def main():
        result = await call_general_model(
            {
                "messages":[HumanMessage(content="Who was Einstein? Give me a 250 words essay.")],
                "collection_name":"847f5e78-25b0-46b0-8188-1ebefd9c2772",
                "enhanced_query":"a 250 words essay about Albert Einstein?"
            },
        )
        print(result)
        
    
    asyncio.run(main())