from langgraph.graph import StateGraph, START, END
# from typing import Optional
from .nodes.call_general_model.main import call_general_model
from .nodes.call_legal_model.main import call_legal_model
from .nodes.search.main import search
from .nodes.reranker.main import reranker
from .nodes.decide_legal.main import decide_legal, classifier
from app.graph.nodes.query_converter.main import convert_query
# from app.graph.nodes.post_response_node import post_response_node
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.checkpoint.redis.aio import AsyncRedisSaver
import os, asyncio
from langchain_core.messages import HumanMessage, AIMessage
from dotenv import load_dotenv
from .schemas import MyMessagesState

async def create_graph(checkpointer):

    
        
    builder = StateGraph(MyMessagesState)
    builder.add_node(call_legal_model)
    builder.add_node(call_general_model)
    builder.add_node(decide_legal)
    builder.add_node(search)
    builder.add_node(reranker)
    # builder.add_node(post_response_node)
    builder.add_node(convert_query)

    

    builder.add_edge(START, "decide_legal")
    builder.add_conditional_edges(
        "decide_legal",
        classifier,
        {
            "question": "convert_query",
            "casual": "call_general_model"
        }
    )
    builder.add_edge("convert_query", "search")
    builder.add_edge("search", "reranker")
    builder.add_edge("reranker", "call_legal_model")
    
    

    graph = builder.compile(
        checkpointer=checkpointer,
    )
    
    return graph



load_dotenv('.env')

collection_name = "847f5e78-25b0-46b0-8188-1ebefd9c2772"
config = {"configurable": {"thread_id": collection_name}}

prompts = [
    # Legal prompts
    "مهریه در قانون ایران چقدر است و شرایط پرداخت آن چگونه است؟",
    "اگر شوهر مهریه همسرش را پرداخت نکند، آیا زن می‌تواند بدون طلاق برای دریافت مهریه اقدام کند و چه مراحلی دارد؟",
    "شرایط تحقق سرقت حدی در قانون مجازات اسلامی چیست؟"
    "مجازات سرقت در قانون مجازات اسلامی ایران چیست و چه شرایطی دارد؟",
    "حقوق کارگر در قرارداد کار موقت چگونه محاسبه می‌شود و بیمه تأمین اجتماعی چقدر است؟",
    "مراحل ثبت سند رسمی ملک در دفترخانه اسناد رسمی چگونه است و چه مدارکی نیاز دارد؟",
    "در قرارداد اجاره، چه مواردی باید قید شود تا از نظر قانونی معتبر باشد؟",
    "در چه مواردی می‌توان قرار بازداشت موقت صادر کرد و مدت آن چقدر است و اعتراض به آن چگونه است؟",

    # General prompts
    "سلام، چطوری؟ امروز روز خوبی برات آرزو می‌کنم",
    "هوای امروز تهران چطوره؟ فردا بارون میاد؟",
    "بهترین دستور پخت قورمه سبزی چیه؟ مواد لازمش رو بگو",
    "فرق بین گوشی سامسونگ و آیفون چیه؟ کدوم رو پیشنهاد می‌دی؟",
    "بهترین فیلم‌های ایرانی سال ۱۴۰۴ کدوم‌ها بودن؟ یکی رو پیشنهاد بده",
]

async def main():
    
    async with AsyncRedisSaver.from_conn_string(
        os.getenv("REDIS_URI"), 
        ttl={"default_ttl": 3600, "refresh_on_read": True}
    ) as redis_cp:
        
        graph = await create_graph(redis_cp)
        
        
        # Invoke the graph
        result = await graph.ainvoke(
            {
                "messages": [HumanMessage(content=prompts[6])],
                "collection_name": collection_name,
            },
            config=config
        )
        
    
if __name__ == "__main__":

    asyncio.run(main())