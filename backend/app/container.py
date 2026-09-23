from dependency_injector import containers, providers
from langchain.chat_models import init_chat_model
from langchain.embeddings import init_embeddings
from tokenizers import Tokenizer
from qdrant_client import AsyncQdrantClient
from redis import Redis
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.services.user import UserService
import os
from openai import AsyncOpenAI



class Container(containers.DeclarativeContainer):
    # Wrap llm in Singleton - GOOD ✅
    gemma3_4B = providers.Singleton(
        init_chat_model,
        model="gemma3_4B",
        model_provider="openai",
        temperature=0.1,
        max_retries=2,
        api_key="not-needed",
        base_url="http://localhost:8087/v1",
    )


    reranker_client = providers.Singleton(
        AsyncOpenAI,
        base_url="http://127.0.0.1:8091/v1",
        api_key="not-needed",
    )

    
    qwen_35 = providers.Singleton(
        init_chat_model,
        model="qwen_35",
        model_provider="openai",
        temperature=0.6,
        top_p=0.95,
        max_retries=2,
        api_key="not-needed",
        base_url="http://localhost:8086/v1",
        extra_body={
            "top_k": 20,
            "chat_template_kwargs": {"enable_thinking": False},
        },
    )

    # Wrap embeddings in Singleton - FIXED ✅
    embedding_model = providers.Singleton(
        init_embeddings,
        model="openai:qwen3_0.6B_gguf",
        # model_provider="openai",
        api_key="not-needed",
        base_url="http://0.0.0.0:8080/v1",
        check_embedding_ctx_length=False,
    )

    tokenizer = providers.Singleton(
        Tokenizer.from_file,
        "app/qwen_tokenizer/tokenizer.json",
        
    )

    

    # Qdrant Client
    qdrant_client = providers.Singleton(
        AsyncQdrantClient,
        host="localhost",
        port=6333,
        https=False,
        api_key="123456789",
    )

    user_service = providers.Singleton(
        UserService,
        qdrant_client=qdrant_client,  # ✅ pass the required dependency
        # redis_client=redis_client,
    )
    # Redis client
    def create_redis():
        return Redis.from_url(os.getenv("REDIS_URI"), decode_responses=True)

    # redis_client = providers.Resource(create_redis)
    # Fixed - use Singleton
    redis_client = providers.Singleton(create_redis)

    # Async Postgres engine
    def create_engine():
        return create_async_engine(os.getenv("ASYNC_DB_URI"), future=True, echo=False)
    

    # Fixed - SQLAlchemy engine is designed to be a singleton
    async_postgres_engine = providers.Singleton(create_engine)

    def create_session_factory(engine):
        return sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


    async_postgres_session_factory = providers.Singleton(
        create_session_factory,
        engine=async_postgres_engine
    )

# Create container instance
container = Container()

# Initialize resources (optional but good practice)
container.init_resources()