import os
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from fastapi import APIRouter, HTTPException

import os, asyncio
from dotenv import load_dotenv

load_dotenv(".env")

router = APIRouter()

@router.get("/{user_id}")
async def get_retrieved_content(
    user_id: str, 
    limit: int = 20, 
    offset: int = 0
):
    """LEGAL RETRIEVED CONTENTS"""
    
    async with AsyncPostgresSaver.from_conn_string(os.getenv("DB_URI")) as pg_saver:
        config = {"configurable": {"thread_id": user_id}}
        current_state = await pg_saver.aget_tuple(config)

        # Case 1: No checkpoint exists for this user
        if current_state is None:
            raise HTTPException(
                status_code=404,
                detail=f"No checkpoint found for user_id: {user_id}"
            )

        # Case 2: Checkpoint exists but no retrieved_content
        channel_values = current_state.checkpoint.get("channel_values", {})
        if "retrieved_content" not in channel_values:
            raise HTTPException(
                status_code=404,
                detail="No retrieved content found for this user"
            )

        text = channel_values["retrieved_content"]

        # Case 3: retrieved_content is None or empty
        if not text:
            raise HTTPException(
                status_code=404,
                detail="Retrieved content is empty"
            )

        replacements = {
            "[Source 1]": "منبع 1",
            "[Source 2]": "منبع 2",
            "[Source 3]": "منبع 3",
            "[Source 4]": "منبع 4",
            "[Source 5]": "منبع 5",
            "Law": "قانون",
            "Book": "کتاب",
            "Chapter": "فصل",
            "Section": "بخش",
            "Subsection": "زیربخش",
            "Article": "ماده",
            "Status": "وضعیت",
            "None": "هیچ",
            "Text": "متن",
        }

        for en, fa in replacements.items():
            text = text.replace(en, fa)

        return {
            "user_id": user_id,
            "retrieved_content": text,
        }


if __name__ == "__main__":
    thread_id = "847f5e78-25b0-46b0-8188-1ebefd9c2772"
    asyncio.run(get_retrieved_content(thread_id))