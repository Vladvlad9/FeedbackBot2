from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, update, delete, and_

from models import ChatBot, create_async_session
from schemas import ChatSchema, ChatInDBSchema


class CRUDChats(object):

    @staticmethod
    @create_async_session
    async def add(chat: ChatSchema, session: AsyncSession = None) -> ChatInDBSchema | None:
        chats = ChatBot(
            **chat.dict()
        )
        session.add(chats)
        try:
            await session.commit()
        except IntegrityError as e:
            print(e)
        else:
            await session.refresh(chats)
            return ChatInDBSchema(**chats.__dict__)

    @staticmethod
    @create_async_session
    async def get(chat_id: int = None,
                  bot_id: int = None,
                  session: AsyncSession = None) -> ChatInDBSchema | None:
        if chat_id:
            chats = await session.execute(
                select(ChatBot)
                .where(ChatBot.chat_id == chat_id)
            )
        else:
            chats = await session.execute(
                select(ChatBot)
                .where(ChatBot.bot_id == bot_id)
            )
        if chat := chats.first():
            return ChatInDBSchema(**chat[0].__dict__)

    @staticmethod
    @create_async_session
    async def get_all(user_id: int = None, session: AsyncSession = None) -> list[ChatInDBSchema]:
        try:
            chats = await session.execute(
                select(ChatBot).where(ChatBot.user_id == user_id)
                .order_by(ChatBot.id)
            )
            return [ChatInDBSchema(**chat[0].__dict__) for chat in chats]
        except ValidationError as e:
            print(e)

    @staticmethod
    @create_async_session
    async def update(chat: ChatInDBSchema, session: AsyncSession = None) -> None:
        await session.execute(
            update(ChatBot)
            .where(ChatBot.id == chat.id)
            .values(**chat.dict())
        )
        await session.commit()
