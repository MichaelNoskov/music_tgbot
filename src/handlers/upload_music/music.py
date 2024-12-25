from aiogram.filters import Command
from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram import F

from src.handlers.upload_music.router import router
from src.handlers.states.auth import AuthGroup
from src.handlers.states.music import MusicUploadForm
from src.storage.minio_ import upload_music
import aio_pika
import msgpack
from src.storage.rabbit import channel_pool
from aio_pika import ExchangeType


class AudioFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return bool(message.audio)


@router.message(Command('upload_music'), AuthGroup.authorized)
async def music(message: Message, state: FSMContext) -> None:
    await state.set_state(MusicUploadForm.title)
    await message.answer(f'Введи название музыки:')


@router.callback_query(F.data == 'upload_music', AuthGroup.authorized)
async def music(call: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(MusicUploadForm.title)
    await call.message.answer(f'Введи название музыки:')


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
    await upload_music(filepath, file_bytes.getvalue())
    await state.update_data(file_url=filepath)

    form: dict[str, str | int] = {
        field: field_data
        for field, field_data in (await state.get_data()).items()
    }


    # запрос в rabbit для сохранения данных в бд   
    async with channel_pool.acquire() as channel:
        exchange = await channel.declare_exchange('user_music', ExchangeType.DIRECT, durable=True)
    
        queue = await channel.declare_queue('user_ask', durable=True)
        await queue.bind(exchange, 'user_ask')

        form['user_id'] = message.from_user.id
        form['action'] = 'upload_music'

        await exchange.publish(
            aio_pika.Message(
                msgpack.packb(
                    form
                ),
            ),
            'user_ask'
        )

    await message.answer('окей')

    # await redirect_menu(message)
