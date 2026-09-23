from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import os, json
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.checkpoint.redis.aio import AsyncRedisSaver
from langchain_core.messages import HumanMessage
from uuid import uuid4
from dotenv import load_dotenv
import asyncio

from app.graph.main import create_graph as create_main_graph
# from app.utils.clean_checkpoint import clean_checkpoint
from app.utils.my_utils import count_tokens
from app.container import container


load_dotenv(".env")
router = APIRouter(prefix="/chat", tags=["chat"])
tokenizer = container.tokenizer()




@router.websocket("/stream/{collection_name}")
async def websocket_chat_stream(
 websocket: WebSocket, 
                                collection_name: str):
    await websocket.accept()
    print(f"✅ Client connected: {collection_name}")

    REDIS_URI = os.getenv("REDIS_URI")
    current_stream_task = None   # track the currently running stream

    async with AsyncRedisSaver.from_conn_string(
        redis_url=REDIS_URI,
        ttl={"default_ttl": 3600, "refresh_on_read": True},
    ) as redis_cp:
        await redis_cp.asetup()

        # 1. Create both graphs, sharing the same Redis checkpointer
        main_graph = await create_main_graph(redis_cp)
        # side_graph = await create_side_chat_graph(redis_cp)


        graphs = {"main": main_graph, 
                #   "side": side_graph
                  }


        
        # Helper: stream using a specific graph
        async def stream_messages(
            human_input: str,
            message_count: int,
            graph_type: str,
            graph_instance
        ):
            """Background task that streams tokens and saves state for the selected graph."""
            output = ""
            # Build config that includes both thread_id and graph_type
            collection_name_to_pass = collection_name if graph_type == "main" else f"side_{collection_name}"
            
            config = {
                "configurable": {
                    "thread_id": collection_name_to_pass,
                    
                }
            }
                
            try:
                async with asyncio.timeout(180):
                    # Use the selected graph instance
                    async for chunk in graph_instance.astream(
                        {
                            "messages": [HumanMessage(content=human_input)],
                            "collection_name": collection_name_to_pass,   # adapt if side graph expects different keys
                        },
                        config=config,
                        stream_mode="messages"
                    ):
                        if chunk[1]['langgraph_node'] == "call_general_model" or chunk[1]['langgraph_node'] == "call_legal_model" :
                            token_content = chunk[0].content
                            output += token_content
                            await websocket.send_json({
                                "type": "token",
                                "content": token_content,
                                "accumulated": output
                            })

                    
                current_state = await graph_instance.aget_state(config)
                if "retrieved_content" in current_state.values:
                    print("RETRIEVED_CONTENT")
                    print(current_state.values['retrieved_content'])
                    print("RETRIEVED_CONTENT")
                    await websocket.send_json({
                        "type": "retrieved_content",
                        "retrieved_content": current_state.values['retrieved_content'],    
                    })

                token_count = count_tokens(current_state.values['messages'], tokenizer)
                if graph_type == "side":
                    await websocket.send_json({
                        "type": "complete",
                        "token_count": token_count,
                        "storage_status": {
                            "postgres": "not utilized",
                            "qdrant": "not utilized"
                        }
                    })
                elif graph_type == "main":
                    # Stream finished – get final state and persist to Postgres
                    
                    redis_tuple = await redis_cp.aget_tuple(config)
                    checkpoint = redis_tuple.checkpoint

                    # REDIS SIDE CHAT TRUNCATED MESSAGES HANDLING
                    # redis_side_chat_writes = [("message", m) for m in redis_tuple.checkpoint['channel_values']['truncated_messages']]
                    # redis_side_chat_write_config = {
                    #     'configurable': {
                    #         'thread_id': f'side_{collection_name}',
                    #         'checkpoint_ns': '',
                    #         'checkpoint_id': f'side_{redis_tuple.config['configurable']['checkpoint_id']}'
                    #     }
                    # }
                    
                    # redis_side_chat_checkpoint = redis_tuple.checkpoint

                    # clean_checkpoint(redis_side_chat_checkpoint)
                    # redis_side_chat_checkpoint['channel_values']['collection_name'] = f'side_{collection_name}'

                    # await redis_cp.aput(redis_side_chat_write_config, redis_side_chat_checkpoint, {}, {})
                    # await redis_cp.aput_writes(redis_side_chat_write_config, redis_side_chat_writes, task_id=str(uuid4()))

                    redis_write_config = {
                        "configurable": {
                            "thread_id": f"side_{collection_name}",
                            
                        }
                    }
                    # main_graph_state = await main_graph.aget_state(config)
                    
                    # # MUST BE FIXED
                    # await side_graph.aupdate_state(
                    #     config = redis_write_config,
                    #     values = {"truncated_messages": main_graph_state.values['truncated_messages']},
                    #     as_node = "call_model"
                    # )

                    
                    # POSTGRES MESSAGES HANDLING
                    postgres_writes = [("message", m) for m in redis_tuple.checkpoint['channel_values']['messages']]
                    write_config = redis_tuple.config
                    async with AsyncPostgresSaver.from_conn_string(os.getenv("DB_URI")) as pg_cp:
                        await pg_cp.setup()
                        await pg_cp.aput(write_config, checkpoint, {}, {})
                        await pg_cp.aput_writes(write_config, postgres_writes, task_id=str(uuid4()))

                    postgres_status = current_state.values.get("postgres_save", "unknown")
                    qdrant_status = current_state.values.get("qdrant_save", "unknown")
                    

                    await websocket.send_json({
                        "type": "complete",
                        "token_count": token_count,
                        "storage_status": {
                            "postgres": postgres_status,
                            "qdrant": qdrant_status
                        }
                    })
                print(f"✅ Stream completed for {graph_type} message #{message_count}")

            except asyncio.CancelledError:
                print(f"🛑 Stream cancelled for {graph_type} message #{message_count}")
                await websocket.send_json({
                    "type": "stop_ack",
                    "message": "Streaming stopped by user"
                })
                raise
            except asyncio.TimeoutError:
                print(f"⏰ Stream timeout for {graph_type} message #{message_count}")
                await websocket.send_json({
                    "type": "error",
                    "error": "Stream timeout - please try again"
                })
            except Exception as e:
                print(f"❌ Stream error on {graph_type}: {e}")
                import traceback
                traceback.print_exc()
                await websocket.send_json({
                    "type": "error",
                    "error": str(e)
                })

        # Main message loop – always listening
        message_count = 0
        try:
            while True:
                data = await websocket.receive_text()
                try:
                    msg = json.loads(data)
                except json.JSONDecodeError:
                    await websocket.send_json({"type": "error", "error": "Invalid JSON"})
                    continue

                # Handle stop command (same as before)
                if msg.get("type") == "stop":
                    if current_stream_task and not current_stream_task.done():
                        current_stream_task.cancel()
                        await asyncio.sleep(0.1)
                        print("🛑 Stop command received – streaming cancelled")
                    else:
                        await websocket.send_json({"type": "info", "message": "No active stream to stop"})
                    continue

                # Extract the user message and graph type
                human_input = msg.get("message", "")
                if not human_input:
                    continue

                graph_type = msg.get("graph_type", "main")   # default to "main"
                if graph_type not in graphs:
                    await websocket.send_json({
                        "type": "error",
                        "error": f"Unknown graph_type: {graph_type}. Use 'main' or 'side'."
                    })
                    continue

                message_count += 1
                print(f"\n--- New message #{message_count} (graph: {graph_type}) ---")

                # Cancel any ongoing stream before starting a new one
                if current_stream_task and not current_stream_task.done():
                    current_stream_task.cancel()
                    await asyncio.sleep(0.1)
                    print(f"⚠️ Cancelled previous stream for new message #{message_count}")

                # Start streaming with the selected graph
                current_stream_task = asyncio.create_task(
                    stream_messages(human_input, message_count, graph_type, graphs[graph_type])
                )

        except WebSocketDisconnect:
            print(f"🔌 Client disconnected: {collection_name}")
            if current_stream_task and not current_stream_task.done():
                current_stream_task.cancel()
        except Exception as e:
            print(f"💥 Fatal error in main loop: {e}")
            import traceback
            traceback.print_exc()



async def main():
    await websocket_chat_stream(WebSocket, "847f5e78-25b0-46b0-8188-1ebefd9c2772")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())