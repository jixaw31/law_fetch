
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
import os, asyncio
from dotenv import load_dotenv

load_dotenv(".env")

router = APIRouter()

# Response models
class MessageResponse(BaseModel):
    role: str  # "human" or "ai"
    content: str
    node_name: Optional[str] = None
    timestamp: Optional[float] = None
    response_metadata: Optional[dict] = None
    additional_kwargs: Optional[dict] = None


@router.get("/{user_id}")
async def get_messages(
    user_id: str, 
    limit: int = 20, 
    offset: int = 0
):
    """Get messages with pagination (last 'limit' messages by default)"""
    
    async with AsyncPostgresSaver.from_conn_string(os.getenv("DB_URI")) as pg_saver:
        
        
        config = {"configurable": {"thread_id": user_id}}
        
        try:
            # Get the checkpoint tuple which contains pending_writes
            checkpoint_tuple = await pg_saver.aget_tuple(config)
            
            if not checkpoint_tuple:
                return {
                    "user_id": user_id,
                    "error": "No checkpoint found for this conversation",
                    "messages": []
                }
            
            # Extract messages from pending_writes
            # Each pending_write is a tuple: (task_id, channel_name, message)
            pending_writes = checkpoint_tuple.pending_writes if checkpoint_tuple.pending_writes else []
            
            all_messages = []
            for write in pending_writes:
                # write format: (task_id, channel_name, message_content)
                if len(write) >= 3 and write[1] == "message":
                    message = write[2]
                    all_messages.append(message)
            
            if not all_messages:
                return {
                    "user_id": user_id,
                    "message": "No messages found",
                    "messages": []
                }
            
            # Get messages with offset from the end
            start_idx = max(0, len(all_messages) - limit - offset)
            end_idx = len(all_messages) - offset if offset > 0 else len(all_messages)
            messages_subset = all_messages[start_idx:end_idx]
            
            formatted_messages = []
            for msg in messages_subset:
                formatted_messages.append({
                    "role": msg.type,
                    "content": msg.content,
                    "node_name": msg.additional_kwargs.get("node_name") if hasattr(msg, "additional_kwargs") else None,
                    "timestamp": msg.response_metadata.get("timestamp") if hasattr(msg, "response_metadata") else None
                })
            
            return {
                "user_id": user_id,
                "total_messages": len(all_messages),
                "returned_messages": len(formatted_messages),
                "limit": limit,
                "offset": offset,
                "messages": formatted_messages
            }
            
        except Exception as e:
            return {
                "user_id": user_id,
                "error": f"Error: {str(e)}",
                "messages": []
            }


async def main():
    thread_id = "847f5e78-25b0-46b0-8188-1ebefd9c2772"
    
    print("=" * 60)
    print("Testing get_messages function")
    print("=" * 60)
    
    # Test 1: Get last 20 messages (default)
    print("\n📝 Test 1: Get last 20 messages")
    print("-" * 60)
    result = await get_messages(thread_id)
    
    if "error" in result:
        print(f"❌ Error: {result['error']}")
    else:
        
        print(f"📊 Total messages: {result['total_messages']}")
        print(f"📋 Returned: {result['returned_messages']}")
        print(f"🎯 Limit: {result['limit']}, Offset: {result['offset']}")
        print("\n💬 Messages:")
        for i, msg in enumerate(result['messages'], 1):
            node_info = f" [{msg['node_name']}]" if msg['node_name'] else ""
            print(f"{i}. {msg['role']}{node_info}: {msg['content'][:100]}...")
    
    # Test 2: Get last 5 messages
    print("\n" + "=" * 60)
    print("📝 Test 2: Get last 5 messages")
    print("-" * 60)
    result = await get_messages(thread_id, limit=5)
    
    if "error" not in result:
        for i, msg in enumerate(result['messages'], 1):
            print(f"{i}. {msg['role']}: {msg['content'][:100]}...")
    
    # Test 3: Get with offset (skip last 10, get 5)
    print("\n" + "=" * 60)
    print("📝 Test 3: Skip last 10, get 5 messages")
    print("-" * 60)
    result = await get_messages(thread_id, limit=5, offset=10)
    
    if "error" not in result:
        for i, msg in enumerate(result['messages'], 1):
            print(f"{i}. {msg['role']}: {msg['content'][:100]}...")

if __name__ == "__main__":
    asyncio.run(main())
