from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_like_keyboard(has_like: bool, music_id) -> InlineKeyboardMarkup:
    if has_like:
        btn = InlineKeyboardButton(text='❤', callback_data=f'dislike:{music_id}')
    else:
        btn = InlineKeyboardButton(text='🩶', callback_data=f'like:{music_id}')

    return InlineKeyboardMarkup(inline_keyboard=[[btn]])
