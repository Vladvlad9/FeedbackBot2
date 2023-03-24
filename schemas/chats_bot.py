from pydantic import BaseModel, Field


class ChatSchema(BaseModel):
    chat_id: int
    bot_id: int


class ChatInDBSchema(ChatSchema):
    id: int = Field(ge=1)
