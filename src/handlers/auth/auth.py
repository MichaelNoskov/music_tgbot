from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
import aio_pika
from aio_pika import ExchangeType
import msgpack

from src.handlers.auth.router import router
from src.handlers.states.auth import AuthGroup, AuthUserProfileForm
from src.handlers.command.start import menu as redirect_menu
from src.storage.rabbit import channel_pool


@router.message(Command('auth'), AuthGroup.no_authorized)
async def start_auth(message: Message, state: FSMContext) -> None:
    await state.set_state(AuthUserProfileForm.default_name)
    await message.answer(f'Ваше имя в Телеграм: {message.from_user.username}\nОставляем его в качестве имени? (ДА/нет)')


@router.message(AuthUserProfileForm.default_name)
async def process_name(message: Message, state: FSMContext) -> None:
    if message.text.lower() == 'нет':
        await state.set_state(AuthUserProfileForm.username)
        await message.answer('Введите имя:')
        return

    name = message.from_user.username
    await state.update_data(username=name)
    await state.set_state(AuthUserProfileForm.description)
    await message.answer(f'Выбрано имя: {name}\nПоделитесь информацией о себе:')


@router.message(AuthUserProfileForm.username)
async def process_username(message: Message, state: FSMContext) -> None:
    await state.update_data(username=message.text)
    await state.set_state(AuthUserProfileForm.description)
    await message.answer(f'Поделитесь информацией о себе:')


@router.message(AuthUserProfileForm.description)
async def process_description(message: Message, state: FSMContext) -> None:
    await state.update_data(description=message.text)

    form: dict[str, str | int] = {
        field: field_data
        for field, field_data in (await state.get_data()).items()
    }

    await state.set_state(AuthGroup.authorized)

    # запрос в rabbit для сохранения данных в бд   
    async with channel_pool.acquire() as channel:
        exchange = await channel.declare_exchange('user_music', ExchangeType.DIRECT, durable=True)
    
        queue = await channel.declare_queue('user_ask', durable=True)
        await queue.bind(exchange, 'user_ask')
        

        form['id'] = message.from_user.id
        form['action'] = 'create_profile'

        await exchange.publish(
            aio_pika.Message(
                msgpack.packb(
                    form
                ),
            ),
            'user_ask'
        )

    await redirect_menu(message)
