# src/handlers/callback/router.py

from aiogram import Router, types

router = Router()

@router.callback_query()
async def handle_callback(callback_query: types.CallbackQuery):
    await callback_query.answer("Callback received!")
