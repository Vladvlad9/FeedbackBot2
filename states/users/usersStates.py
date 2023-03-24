from aiogram.dispatcher.filters.state import StatesGroup, State


class UserStates(StatesGroup):
    WelcomeText = State()
    Newsletters = State()