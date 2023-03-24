import asyncio
import logging

from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import BotKicked, ChatNotFound, MessageToForwardNotFound

from config import CONFIG
from crud import CRUDUsers, CRUDBots, CRUDChats
from keyboards.inline.users.mainForm import main_cb, MainForms
from schemas import UserSchema, BotTGSchema, ChatSchema
from states.users import UserStates
from utils.set_bot_commands import set_default_commands
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


async def main_bot(token: str):

    bot = Bot(token)
    # Create a dispatcher instance for the bot
    dp = Dispatcher(bot, storage=MemoryStorage())

    async def set_commands(bot: Bot):
        commands = [
            types.BotCommand(command="/start", description="Start the bot"),
            types.BotCommand(command="/addbot", description="Show help message")
        ]
        await bot.set_my_commands(commands)

    @dp.message_handler(commands=['addbot'])
    async def add_bot(message: types.Message):
        # Get the token from the command argument
        token = message.get_args()
        try:
            # Create a new bot instance with the provided token
            new_bot = Bot(token)
            bot_user = await new_bot.get_me()
            if token in CONFIG.BOT.TOKEN_ALL:
                await message.answer("This bot is already running!")
                return
            else:
                CONFIG.BOT.TOKEN_ALL.append(token)
                await CRUDBots.add(bot=BotTGSchema(user_id=message.from_user.id,
                                                   bot_id=bot_user.id,
                                                   bot_token=token)
                                   )
                # Send a success message
                await message.answer(f"Successfully added bot {bot_user.username}")
                asyncio.create_task(start_bot(token))
        except Exception as e:
            print(e)
            # Send an error message if the token is invalid
            await message.answer("Error: Invalid token")

    # Define message handlers for the bot
    @dp.message_handler(commands=['start'])
    async def start(message: types.Message):
        bot_user = await bot.get_me()
        user = await CRUDUsers.get(user_id=message.from_user.id)
        if user:
            await message.delete()
            await message.answer(text=f"Добро пожаловать в Бот обратной связи {bot_user.username}!",
                                 reply_markup=await MainForms.main_menu_ikb(user_id=message.from_user.id))
        else:
            await CRUDUsers.add(user=UserSchema(user_id=message.from_user.id,
                                                chat_id=0,
                                                use_bot_id=int(bot_user.id)
                                                )
                                )
            await message.delete()
            await message.answer(f"Добро пожаловать в Бот обратной связи {bot_user.username}!",
                                 reply_markup=await MainForms.main_menu_ikb(user_id=message.from_user.id))
            logger.info(f"User {message.from_user.username} registration")

    @dp.callback_query_handler(main_cb.filter())
    @dp.callback_query_handler(main_cb.filter(), state=UserStates.all_states)
    async def process_callback(callback: types.CallbackQuery, state: FSMContext = None):
        await MainForms.process(callback=callback, state=state)

    @dp.message_handler(state=UserStates.all_states, content_types=["text"])
    async def process_message(message: types.Message, state: FSMContext):
        await MainForms.process(message=message, state=state)

    await set_commands(bot)
    # Start polling for the bot
    await dp.start_polling()


async def start_bot(token: str):
    # Create a bot instance
    bot = Bot(token)
    # Create a dispatcher instance for the bot
    dp = Dispatcher(bot, storage=MemoryStorage())

    async def set_commands(bot: Bot):
        commands = [
            types.BotCommand(command="/start", description="Start the bot"),
            types.BotCommand(command="/lol", description="Show help message")
        ]
        await bot.set_my_commands(commands)

    @dp.message_handler(commands=['ban'])
    async def ban(message: types.Message):
        if message.reply_to_message:
            try:
                user = await CRUDUsers.get(user_id=message.from_user.id)

                if user:
                    get_bot = await CRUDBots.get(user_id=user.user_id)
                    current_bot = Bot(token=get_bot.bot_token)

                    user.ban = True
                    await CRUDUsers.update(user=user)
                    await message.answer(text="Пользователь забанен")
                    await current_bot.send_message(text="Вас забанили в боте",
                                                   chat_id=user.user_id)
                else:
                    await message.answer(text="Такого пользователя не существует")
            except Exception as e:
                print(e)

    @dp.message_handler(commands=['unban'])
    async def ban(message: types.Message):
        if message.reply_to_message:
            try:
                user = await CRUDUsers.get(user_id=message.from_user.id)

                if user:
                    get_bot = await CRUDBots.get(user_id=user.user_id)
                    current_bot = Bot(token=get_bot.bot_token)

                    user.ban = False
                    await CRUDUsers.update(user=user)
                    await message.answer(text="Пользователь разбанен")
                    await current_bot.send_message(text="Вас разбанили в боте",
                                                   chat_id=user.user_id)
                else:
                    await message.answer(text="Такого пользователя не существует")
            except Exception as e:
                print(e)

    # Define message handlers for the bot
    @dp.message_handler(commands=['start'])
    async def start(message: types.Message):
        user = await CRUDUsers.get(user_id=message.from_user.id)
        bot_user = await bot.get_me()
        if user:
            get_bot_tg = await CRUDBots.get(bot_id=bot_user.id)
            if get_bot_tg.welcome_text != "None":
                await message.answer(text=get_bot_tg.welcome_text)
            else:
                await message.answer(f"Hello from {bot_user.username}!")
        else:
            # проверку на то что состоит ли бот в чате
            get_chat = await CRUDChats.get(bot_id=int(bot_user.id))
            await CRUDUsers.add(user=UserSchema(user_id=message.from_user.id,
                                                chat_id=get_chat.chat_id,
                                                use_bot_id=int(bot_user.id)
                                                )
                                )
            await message.answer(text=f"Hello from {bot_user.username}!")
            logger.info(f"User {message.from_user.id} registration")

    @dp.message_handler(content_types=["left_chat_member"])
    async def delete_chat(message: types.Message):
        if message.left_chat_member.is_bot:
            name_bot = message.left_chat_member.username
            text = f"Бот <a href='t.me/{name_bot}'>{name_bot}</a> удален из группы"
            await bot.send_message(text=text,
                                   chat_id=message.from_user.id,
                                   parse_mode="HTML")

    @dp.message_handler(content_types=["new_chat_members"])
    async def add_chat(message: types.Message):
        if message.new_chat_members[0].is_bot:
            CONFIG.CHAT.append(str(message.chat.id))
            name_bot = message.new_chat_members[0].username
            text = f"Бот <a href='t.me/{name_bot}'>{name_bot}</a> добавлен в группу"
            await bot.send_message(text=text,
                                   chat_id=message.from_user.id,
                                   parse_mode="HTML")
            await CRUDChats.add(chat=ChatSchema(chat_id=message.chat.id,
                                                bot_id=int(message.new_chat_members[0].id))
                                )
            logger.info(f"Bot {name_bot} add group")
            #сделать оповещение польователям что боата добавлили в группу и они могут писать

    @dp.message_handler(content_types="any")
    async def echo(message: types.Message):
        if not message.reply_to_message:
            try:
                user = await CRUDUsers.get(user_id=message.from_user.id)
                if user.chat_id == 0:
                    get_bot = await bot.get_me()
                    get_chat = await CRUDChats.get(bot_id=get_bot.id)
                    if get_chat:
                        user.chat_id = get_chat.chat_id
                        await CRUDUsers.update(user=user)
                if user:
                    if user.ban:
                        await message.answer(text="Вы забанены в боте!")
                    else:
                        await bot.forward_message(chat_id=user.chat_id,
                                                  from_chat_id=message.from_user.id,
                                                  message_id=message.message_id)
                else:
                    await message.answer(text='бот не найден')
            except BotKicked as e:
                print(f'BotKicked {e}')
                await message.answer(text='Данный бот не добавлен в чат')
            except ChatNotFound as e:
                print(e)
                await message.answer(text='Данный бот не добавлен в чат')
            except MessageToForwardNotFound as e:
                print(e)
            except Exception as e:
                await message.answer(text='Данный бот не добавлен в чат')
        else:
            try:
                get_user_id = await CRUDUsers.get(user_id=message.reply_to_message.forward_from.id)
                if get_user_id:
                    await bot.send_message(chat_id=message.reply_to_message.forward_from.id,
                                           text=message.text)
                else:
                    await message.answer(text="Пользователя не найдено")
            except Exception as e:
                print(e)

    await set_commands(bot)
    # Start polling for the bot
    await dp.start_polling()


async def main():
    # Create tasks for each bot
    get_token = await CRUDBots.get_all()
    for token in get_token:
        CONFIG.BOT.TOKEN_ALL.append(token.bot_token)

    tasks = [asyncio.create_task(start_bot(token)) for token in CONFIG.BOT.TOKEN_ALL]
    tasks.append(asyncio.create_task(main_bot(CONFIG.BOT.TOKEN_MAIN)))

    await asyncio.gather(*tasks)


if __name__ == '__main__':
    asyncio.run(main())
