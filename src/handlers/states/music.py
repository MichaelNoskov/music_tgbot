from aiogram.fsm.state import State, StatesGroup


class MusicUploadForm(StatesGroup):
    title = State()
    genre = State()
    file = State()
    nothing = State()
