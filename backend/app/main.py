from fastapi import FastAPI


from contextlib import asynccontextmanager

from fastapi.middleware.cors import CORSMiddleware
from app.routers.ws_chat import router as ws_router
from app.routers.users import router as user_router
from app.routers.messages import router as messages_router
from app.routers.fetch_retrieved import router as fetch_retrieved_router
from app.utils.native_auth import SwaggerAuthMiddleware
from app.container import container


container.wire(
    modules=[
        "app.routers.users",
        "app.routers.ws_chat",
        "app.routers.messages",
    ]
)



# Define lifespan for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize resources
    print("Initializing container resources...")
    container.init_resources()
    print("Container resources initialized successfully!")
    
    # You can also test if models are working
    try:
        llm = container.qwen_35()
        test_response = await llm.ainvoke("Say 'OK'")
        if test_response.content:
            print(f"✅ LLM ready: {llm.model_name if hasattr(llm, 'model_name') else 'configured'}")
        
        embedding_model = container.embedding_model()
        test_embedding = await embedding_model.aembed_query("test")
        if test_embedding and len(test_embedding) > 0:
            print(f"✅ embedding_model ready (dimension: {len(test_embedding)})")
        
        qdrant_client = container.qdrant_client()
        print(f"✅ Qdrant Client ready")
        
        # # ✅ CORRECT: Get the deduplicator instance (it already has the pool injected)
        # deduplicator = container.deduplicator()
        # print(f"✅ deduplicator ready")
        
        # # ✅ CORRECT: Call ensure_extensions on the deduplicator instance
        # await deduplicator.ensure_extensions()
        
    except Exception as e:
        print(f"⚠️ Warning: Model test failed: {e}")
    
    yield  # This is where the app runs
    
    # Shutdown: Clean up resources if needed
    print("Shutting down container resources...")
    # Add any cleanup code here if needed

# Create FastAPI app with lifespan
app = FastAPI(
    title="LangChain API",
    description="API with LLM and Embeddings",
    version="1.0.0",
    lifespan=lifespan
)

origins = [
    "http://192.168.1.104:3000",
    "http://localhost:3000",     # Next.js default port
    "http://localhost:3001",     # Alternative Next.js port
    "http://127.0.0.1:3000",     # Localhost with IP
    "http://localhost:8000",     # Your FastAPI server (if needed)
    "http://127.0.0.1:8000",     # FastAPI with IP
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,           # List of allowed origins
    allow_credentials=True,          # Allow cookies/auth headers
    allow_methods=["*"],             # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],             # Allow all headers
    expose_headers=["*"],            # Expose all headers to client
    max_age=3600,                    # Cache preflight requests for 1 hour
)
app.add_middleware(SwaggerAuthMiddleware)

app.container = container

# Include the WebSocket router
app.include_router(ws_router)
app.include_router(user_router, prefix="/api/auth")
app.include_router(messages_router, prefix="/api/messages")
app.include_router(fetch_retrieved_router, prefix="/api/fetch_retrieved")
# app.include_router(side_messages_router, prefix="/api/side-messages")


    
