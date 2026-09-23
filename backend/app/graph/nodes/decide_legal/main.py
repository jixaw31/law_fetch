import asyncio
from app.container import container 
from ...schemas import MyMessagesState
from .sys_message import Classification, classifier_system_message

gemma3 = container.qwen_35()
gemma3_with_structured_output = gemma3.with_structured_output(Classification)

async def decide_legal(state: MyMessagesState):
    print("decide_legal".upper())
    last_human_message = [m for m in state['messages'] if m.type=="human"][-1]
    res = await gemma3_with_structured_output.ainvoke([classifier_system_message, last_human_message])
    print(res)
    
    return {"decision": res.category}







async def classifier(state: MyMessagesState):
    print("classifier".upper())
    
    if state['decision'] == "question":
        print("question route")
        return "question"
    else:
        print("casual route")
        return "casual"






if __name__ == "__main__":
    asyncio.run(decide_legal({}))