from pydantic import BaseModel, Field


class UserSchema(BaseModel):
    user_id: int = Field(ge=1)
    chat_id: int
    use_bot_id: int
    block: bool = Field(default=False)
    ban: bool = Field(default=False)


class UserInDBSchema(UserSchema):
    id: int = Field(ge=1)
