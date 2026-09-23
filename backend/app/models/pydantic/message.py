from pydantic import BaseModel

class Message(BaseModel):
    """
    Model for a single message.
    """
    text: str

class MessageRead(BaseModel):
    # id: str
    type: str
    content: str