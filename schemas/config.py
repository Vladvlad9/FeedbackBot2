from pydantic import BaseModel


class BotSchema(BaseModel):
    TOKEN_MAIN: str
    TOKEN_ALL: list[str]
    ADMINS: list[int]


class ConfigSchema(BaseModel):
    BOT: BotSchema
    DATABASE: str
    CHAT: list[str]
