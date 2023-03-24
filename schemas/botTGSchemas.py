from pydantic import BaseModel, Field
from datetime import datetime


class BotTGSchema(BaseModel):
    user_id: int = Field(ge=1)
    bot_id: int = Field(ge=1)
    bot_token: str
    date_created: datetime = Field(default=datetime.now())
    welcome_text: str = Field(default=None)


class BotTGInDBSchema(BotTGSchema):
    id: int = Field(ge=1)
