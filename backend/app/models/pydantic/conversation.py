from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime, timezone
import uuid




class ConversationCreate(BaseModel):
    """
    Base model for conversation data.
    """
    id: str
    title: str
    total_input_tokens: int = 0
    total_completion_tokens: int = 0
    total_summarization_input_tokens: int
    total_summarization_output_tokens: int
    embedding_tokens: int
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))
    user_id: str
    collection_name: str 



class ConversationRead(BaseModel):
    id: str
    title: str
    total_input_tokens: int
    total_completion_tokens: int
    total_summarization_input_tokens: int
    total_summarization_output_tokens: int
    embedding_tokens: int
    created_at: datetime
    user_id: str
    collection_name: Optional[str] = None

    model_config = {
        "from_attributes": True  # enables ORM model parsing
    }


class NewConversationRequest(BaseModel):
    """
    Data model for creating a new conversation.
    """
    title: str
    user_id: str