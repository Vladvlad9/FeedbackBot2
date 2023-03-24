from datetime import datetime

from sqlalchemy import Column, TIMESTAMP, DateTime, VARCHAR, Integer, Boolean, Text, ForeignKey, CHAR, BigInteger, \
    SmallInteger
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__: str = "users"

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger)
    chat_id = Column(BigInteger)
    block = Column(Boolean)
    ban = Column(Boolean)
    use_bot_id = Column(BigInteger)


class BotTG(Base):
    __tablename__: str = "bots_tg"

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger)
    bot_id = Column(BigInteger)
    bot_token = Column(Text)
    date_created = Column(TIMESTAMP, default=datetime.now())
    welcome_text = Column(Text, default="None")


class ChatBot(Base):
    __tablename__: str = "chats_bot"

    id = Column(Integer, primary_key=True)
    chat_id = Column(BigInteger)
    bot_id = Column(BigInteger)

