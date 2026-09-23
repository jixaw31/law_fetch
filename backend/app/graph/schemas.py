from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages
from typing import Annotated
from langgraph.graph import MessagesState



class MyMessagesState(MessagesState):
    collection_name: str 
    retrieved_content: str
    enhanced_queries: dict
    laws_points: list = []
    law_QA_points: list = []
    hybrid_points: list = []
    reranked_points: dict = {}
    decision: str
    postgres_save: str = None
    qdrant_save:str = None
    neo4j_save:str=None
    truncated_messages: Annotated[list[AnyMessage], add_messages] = []
