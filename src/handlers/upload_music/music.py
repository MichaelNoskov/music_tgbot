from aiogram.filters import Command
from aiogram.filters import BaseFilter
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from src.handlers.upload_music.router import router
from src.handlers.states.auth import AuthGroup
from src.handlers.states.music import MusicUploadForm
from src.handlers.command.start import menu as redirect_menu
from src.storage.minio_ import upload_music


class AudioFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return bool(message.audio)


@router.message(Command('upload_music'), AuthGroup.authorized)
async def music(message: Message, state: FSMContext) -> None:
    await state.set_state(MusicUploadForm.title)
    await message.answer(f'Введи название музыки:')


@router.message(MusicUploadForm.title)
async def process_title(message: Message, state: FSMContext) -> None:
    await state.update_data(title=message.text)
    await state.set_state(MusicUploadForm.genre)
    await message.answer(f'Введи название жанра:')


@router.message(MusicUploadForm.genre)
async def process_genre(message: Message, state: FSMContext) -> None:
    await state.update_data(genre=message.text)
    await state.set_state(MusicUploadForm.file)
    await message.answer(f'Отправь файл с музыкой')


@router.message(AudioFilter(), MusicUploadForm.file)
async def process_file(message: Message, state: FSMContext) -> None:

    audio_file_id = message.audio.file_id

    bot = message.bot
    file_info = await bot.get_file(audio_file_id)
    file_bytes = await bot.download_file(file_info.file_path)

    form: dict[str, str | int] = {
        field: field_data
        for field, field_data in (await state.get_data()).items()
    }

    # сохранение музыки в minio

    filepath = f'{message.from_user.id}_{form["genre"]}_{form["title"]}.mp3'

    await state.update_data(file=filepath)

    form: dict[str, str | int] = {
        field: field_data
        for field, field_data in (await state.get_data()).items()
    }

    await upload_music(filepath, file_bytes.getvalue())

    await state.set_state(MusicUploadForm.nothing)

    # запрос в rabbit для сохранения данных в бд   

    await message.answer('окей')

    # await redirect_menu(message)
