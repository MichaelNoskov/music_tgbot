from aiogram.fsm.state import State, StatesGroup


class AuthGroup(StatesGroup):
    no_authorized = State()
    authorized = State()


class AuthUserProfileForm(StatesGroup):
    default_name = State()
    username = State()
    description = State()
