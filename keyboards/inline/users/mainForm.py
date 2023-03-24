from aiogram import Bot
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.exceptions import ChatNotFound

from crud import CRUDBots, CRUDChats, CRUDUsers
import requests

from states.users import UserStates

main_cb = CallbackData("main", "target", "action", "id", "editId")


class MainForms:
    @staticmethod
    async def back_ikb(target: str, action: str, bot_name: str = "", bot_id: int = 0) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="◀️ Назад", callback_data=main_cb.new(target, action, bot_id, bot_name))
                ]
            ]
        )

    @staticmethod
    async def main_menu_ikb(user_id: int) -> InlineKeyboardMarkup:
        data_main_menu = {
            "👨‍💻 Добавить бот": {"target": "AddBot", "action": "get_AddBot", "id": user_id, "editId": 0},
            "🤖 Мои боты": {"target": "MyBots", "action": "get_MyBots", "id": user_id, "editId": 0},
        }
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text=str(name_menu),
                                         callback_data=main_cb.new(target=target_menu['target'],
                                                                   action=target_menu['action'],
                                                                   id=target_menu['id'],
                                                                   editId=target_menu['editId']
                                                                   )
                                         )
                ] for name_menu, target_menu in data_main_menu.items()
            ]
        )

    @staticmethod
    async def get_my_bots(user_id: int) -> InlineKeyboardMarkup:
        my_bots = await CRUDBots.get_all(user_id=user_id)
        get_bot = []
        name_bot = {}
        for bot in my_bots:
            if bot.bot_token != "None":
                get_bot.append(bot)

        # https://t.me/+r-qGqZ7b1DBmN2Yy
        for bots in get_bot:
            data_bot = requests.get(f"https://api.telegram.org/bot{str(bots.bot_token)}/getMe")
            get_data_bot = data_bot.json()
            name_bot[get_data_bot['result']['username']] = {"bot_id": f"{bots.id}"}

        return InlineKeyboardMarkup(
            inline_keyboard=[
                                [
                                    InlineKeyboardButton(text=name_menu,
                                                         callback_data=main_cb.new(target="MyBots",
                                                                                   action="get_ShowBot",
                                                                                   id=bot_items['bot_id'],
                                                                                   editId=str(name_menu)))
                                ] for name_menu, bot_items in name_bot.items()
                            ] +
                            [
                                [
                                    InlineKeyboardButton(text="◀️ Назад", callback_data=main_cb.new(target="MainMenu",
                                                                                                    action="get_MainMenu",
                                                                                                    id=user_id,
                                                                                                    editId=""))
                                ]
                            ]
        )

    @staticmethod
    async def settings_current_bot(bot_id: int) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="☠️ Заблокировать пользователя",
                                         callback_data=main_cb.new(target="MyBots",
                                                                   action="BlockedUser",
                                                                   id=bot_id,
                                                                   editId=""))
                ],
                [
                    InlineKeyboardButton(text="📅 Рассылка",
                                         callback_data=main_cb.new(target="MyBots",
                                                                   action="NewslettersBot",
                                                                   id=bot_id,
                                                                   editId="")),
                    InlineKeyboardButton(text="📈 Статистика",
                                         callback_data=main_cb.new(target="MyBots",
                                                                   action="StatisticsBot",
                                                                   id=bot_id,
                                                                   editId=""))
                ],
                [
                    InlineKeyboardButton(text="📝 Текст приветствия",
                                         callback_data=main_cb.new(target="MyBots",
                                                                   action="WelcomeText",
                                                                   id=bot_id,
                                                                   editId="")),
                    InlineKeyboardButton(text="💬 Чаты",
                                         callback_data=main_cb.new(target="MyBots",
                                                                   action="AddChat",
                                                                   id=bot_id,
                                                                   editId=""))
                ],
                [
                    InlineKeyboardButton(text="◀️ Назад",
                                         callback_data=main_cb.new(target="MyBots",
                                                                   action="get_MyBots",
                                                                   id=0,
                                                                   editId=""
                                                                   )
                                         )
                ]
            ]
        )

    @staticmethod
    async def approve_ikb(user_id: int, bot_id: int) -> InlineKeyboardMarkup:
        data_main_menu = {
            "Да": {"target": "MyBots", "action": "AddWelcomeTxt", "id": user_id, "editId": bot_id},
            "Нет": {"target": "MyBots", "action": "get_MyBots", "id": user_id, "editId": bot_id},
        }
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text=str(name_menu),
                                         callback_data=main_cb.new(target=target_menu['target'],
                                                                   action=target_menu['action'],
                                                                   id=target_menu['id'],
                                                                   editId=""
                                                                   )
                                         ) for name_menu, target_menu in data_main_menu.items()
                ]
            ]
        )

    @staticmethod
    async def get_chat(len_users: int, first: int, bot_id: int, message):
        get_bot = await CRUDBots.get(id=bot_id)
        users = await CRUDUsers.get_all(bot_id=get_bot.bot_id)

        my_bot = Bot(token=get_bot.bot_token)
        count = first
        try:
            if len_users == count:
                return
            else:
                for user in users[first: len_users]:
                    await my_bot.send_message(text=message.text,
                                              chat_id=user.user_id)
                    count += 1
        except ChatNotFound:
            users[count].block = True
            await CRUDUsers.update(user=users[count])
            count += 1
            await MainForms.get_chat(first=count, len_users=len_users, message=message, bot_id=bot_id)

    @staticmethod
    async def process(callback: CallbackQuery = None, message: Message = None, state: FSMContext = None) -> None:
        if callback:
            if callback.data.startswith("main"):
                data = main_cb.parse(callback_data=callback.data)
                if data.get("target") == "MainMenu":
                    if data.get("action") == "get_MainMenu":
                        await callback.message.edit_text(text="Добро пожаловать в Бот обратной связи",
                                                         reply_markup=await MainForms.main_menu_ikb(
                                                             user_id=callback.from_user.id)
                                                         )

                elif data.get("target") == "AddBot":
                    if data.get("action") == "get_AddBot":
                        text = "Чтобы подключить бот, вам нужно выполнить два действия:\n\n" \
                               "1. Перейдите в @BotFather и создайте новый бот\n" \
                               "2. После создания бота вы получите токен (12345:6789ABCDEF) — " \
                               "скопируйте и напишите в этот чат" \
                               "/add_bot (Ваш токен)\n\n" \
                               "Важно: не подключайте боты, которые уже используются другими сервисами " \
                               "(Controller Bot, разные CRM и т.д.)"

                        await callback.message.edit_text(text=text,
                                                         reply_markup=await MainForms.back_ikb(
                                                             target="MainMenu",
                                                             action="get_MainMenu")
                                                         )

                elif data.get("target") == "MyBots":
                    if data.get("action") == "get_MyBots":
                        await callback.message.edit_text(text="Выберите бот из списка ниже.",
                                                         reply_markup=await MainForms.get_my_bots(
                                                             user_id=callback.from_user.id)
                                                         )

                    elif data.get("action") == "get_ShowBot":

                        bot_id = int(data.get("id"))
                        bot_name = data.get("editId")

                        if bot_name == "":
                            get_bot = await CRUDBots.get(id=bot_id)
                            my_bot = Bot(token=get_bot.bot_token)
                            get_bot = await my_bot.get_me()
                            bot_name = get_bot.username

                        await callback.message.edit_text(text=f"Управление ботом <a href='t.me/{bot_name}'>{bot_name}</a>",
                                                         reply_markup=await MainForms.settings_current_bot(
                                                             bot_id=bot_id),
                                                         parse_mode="HTML")

                    elif data.get("action") == "BlockedUser":
                        bot_id = int(data.get("id"))
                        await callback.message.edit_text(
                            text="Что бы забанить пользователя необходимо в чате нажать 'Ответить' "
                                 "затем написать <i>/ban</i>\n\n"
                                 "Что бы разбанить пользователя необходимо в чате нажать 'Ответить' "
                                 "затем написать <i>/unban</i>\n\n"
                                 "После чего пользователю будет запрещено/разрешено писать в боте",
                            reply_markup=await MainForms.back_ikb(target="MyBots",
                                                                  action="get_ShowBot",
                                                                  bot_id=bot_id),
                            parse_mode="HTML"
                            )

                    elif data.get("action") == "NewslettersBot":
                        await state.update_data(bot_id=int(data.get("id")))
                        await callback.message.edit_text(text="Введите сообщение для рассылки")
                        await UserStates.Newsletters.set()

                    elif data.get("action") == "StatisticsBot":
                        bot_id = int(data.get("id"))
                        get_bot = await CRUDBots.get(id=bot_id)
                        users = await CRUDUsers.get_all(bot_id=get_bot.bot_id)
                        get_ban_bot = await CRUDUsers.get_all(ban=True)
                        get_blocked_bot = await CRUDUsers.get_all(block=True)

                        text = "📈 Статистика бота\n\n" \
                               f"❗️ Количество человек в боте : {len(users)}\n" \
                               f"🚫 Количество забаненых в чате : {len(get_ban_bot)}\n" \
                               f"☠️ Количество человек которые удалили/остановили бота : {len(get_blocked_bot)}\n\n" \
                               f"<i>Счетчик тех, кто заблокировал бот, обновляется после каждой рассылки.</i>"

                        await callback.message.edit_text(text=text,
                                                         reply_markup=await MainForms.back_ikb(
                                                             target="MyBots",
                                                             action='get_ShowBot',
                                                             bot_id=bot_id),
                                                         parse_mode="HTML")

                    elif data.get("action") == "WelcomeText":
                        bot_id = int(data.get('id'))
                        #await state.update_data(any_bot_id=bot_id)
                        get_bot = await CRUDBots.get(id=bot_id)
                        if get_bot:
                            welcome_txt = get_bot.welcome_text
                            await state.update_data(any_bot_id=bot_id)
                            if welcome_txt == "None":
                                await callback.message.edit_text(text="У вас не добавлен стартовый текст\n"
                                                                      "Желаете добавить новый?",
                                                                 reply_markup=await MainForms.approve_ikb(
                                                                     user_id=callback.from_user.id,
                                                                     bot_id=bot_id)
                                                                 )
                            else:
                                await callback.message.edit_text(text="Ваш стартовый текст:\n\n"
                                                                      f"{welcome_txt}\n\n"
                                                                      f"Желеаете добавить новый?",
                                                                 reply_markup=await MainForms.approve_ikb(
                                                                     user_id=callback.from_user.id,
                                                                     bot_id=bot_id)
                                                                 )
                        else:
                            await callback.message.edit_text(text="Бота не найдено!",
                                                             reply_markup=await MainForms.back_ikb(
                                                                 action="get_MyBots",
                                                                 target="MyBots")
                                                             )

                    elif data.get("action") == "AddChat":
                        bot_id = int(data.get('id'))
                        get_bot = await CRUDBots.get(id=bot_id)

                        if get_bot:
                            get_chat_bot = await CRUDChats.get(bot_id=get_bot.bot_id)
                            if get_chat_bot:
                                my_bot = Bot(token=get_bot.bot_token)
                                get_chat = await my_bot.get_chat(chat_id=get_chat_bot.chat_id)
                                await callback.message.edit_text(text=f"Бот подключен к группе: "
                                                                      f"<a href='https://t.me/{get_chat_bot.chat_id}'>{get_chat.title}</>",
                                                                 reply_markup=await MainForms.back_ikb(
                                                                     target="MyBots",
                                                                     action='get_ShowBot',
                                                                     bot_id=bot_id),
                                                                 parse_mode="HTML")
                            else:
                                await callback.message.edit_text(text="Этот бот не добавлен в чаты, "
                                                                      "поэтому все сообщения будут "
                                                                      "приходить в диалог с ботом.\n\n"
                                                                      "Чтобы подключить чат — добавьте бот "
                                                                      "как нового участника.",
                                                                 reply_markup=await MainForms.back_ikb(
                                                                     target="MyBots",
                                                                     action="get_ShowBot",
                                                                     bot_id=bot_id)
                                                                 )
                        else:
                            await callback.message.edit_text(text="Бот не найден!")

                    elif data.get("action") == "AddWelcomeTxt":
                        await UserStates.WelcomeText.set()
                        await callback.message.edit_text(text="Введите тест")

        if message:
            if state:
                if await state.get_state() == "UserStates:WelcomeText":
                    try:
                        data = await state.get_data()
                        get_bot = await CRUDBots.get(id=int(data["any_bot_id"]))
                        get_bot.welcome_text = message.text
                        await CRUDBots.update(bot=get_bot)
                        await message.answer(text="Стартовый текст успешно изменен на\n\n"
                                                  f"{message.text}",
                                             reply_markup=await MainForms.main_menu_ikb(user_id=message.from_user.id)
                                             )
                        await state.finish()
                    except Exception as e:
                        print(e)
                        await message.answer(text="Возникла ошибка при изменении текста\n\n"
                                                  "Попробуйте еще раз добавить тест",
                                             reply_markup=await MainForms.main_menu_ikb(user_id=message.from_user.id)
                                             )

                elif await state.get_state() == "UserStates:Newsletters":
                    try:
                        data = await state.get_data()
                        get_bot = await CRUDBots.get(id=int(data.get('bot_id')))
                        users = await CRUDUsers.get_all(bot_id=get_bot.bot_id)
                        await MainForms.get_chat(len_users=len(users), first=0, bot_id=int(data.get('bot_id')),
                                                 message=message)
                        await message.answer(text='Рассылка успешна произведена')
                        await state.finish()
                    except ChatNotFound as e:
                        print(e)
                    except Exception as e:
                        print(e)
                        await message.answer(text="Рассылка не произведена")
                        await state.finish()
