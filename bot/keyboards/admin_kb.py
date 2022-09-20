from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup


def start_kb_admin():
    playlist = KeyboardButton("Merge playlist[Admin]")
    link = KeyboardButton("Merge links[Admin]")
    keyboard = ReplyKeyboardMarkup(
        resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(playlist, link)
    return keyboard


def yes_no():
    keyboard = InlineKeyboardMarkup(row_width=1)
    yes = InlineKeyboardButton("Yes", callback_data="yes")
    no = InlineKeyboardButton("No", callback_data="no")
    keyboard.add(yes, no)
    return keyboard
