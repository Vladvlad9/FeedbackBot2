from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, update, delete, and_

from models import BotTG, create_async_session
from schemas import BotTGSchema, BotTGInDBSchema


class CRUDBots(object):

    @staticmethod
    @create_async_session
    async def add(bot: BotTGSchema, session: AsyncSession = None) -> BotTGInDBSchema | None:
        bots = BotTG(
            **bot.dict()
        )
        session.add(bots)
        try:
            await session.commit()
        except IntegrityError as e:
            print(e)
        else:
            await session.refresh(bots)
            return BotTGInDBSchema(**bots.__dict__)

    @staticmethod
    @create_async_session
    async def get(id: int = None,
                  bot_id: int = None,
                  bot_token: str = None,
                  user_id: int = None,
                  session: AsyncSession = None) -> BotTGInDBSchema | None:
        if bot_id:
            bots = await session.execute(
                select(BotTG)
                .where(BotTG.bot_id == bot_id)
            )
        elif id:
            bots = await session.execute(
                select(BotTG)
                .where(BotTG.id == id)
            )
        elif user_id:
            bots = await session.execute(
                select(BotTG)
                .where(BotTG.user_id == user_id)
            )
        else:
            bots = await session.execute(
                select(BotTG)
                .where(BotTG.bot_token == bot_token)
            )
        if bot := bots.first():
            return BotTGInDBSchema(**bot[0].__dict__)

    @staticmethod
    @create_async_session
    async def get_all(user_id: int = None, session: AsyncSession = None) -> list[BotTGInDBSchema]:
        try:
            if user_id:
                bots = await session.execute(
                    select(BotTG).where(BotTG.user_id == user_id)
                    .order_by(BotTG.id)
                )
            else:
                bots = await session.execute(
                    select(BotTG)
                )
            return [BotTGInDBSchema(**bot[0].__dict__) for bot in bots]
        except ValidationError as e:
            print(e)

    @staticmethod
    @create_async_session
    async def update(bot: BotTGInDBSchema, session: AsyncSession = None) -> None:
        await session.execute(
            update(BotTG)
            .where(BotTG.id == bot.id)
            .values(**bot.dict())
        )
        await session.commit()
