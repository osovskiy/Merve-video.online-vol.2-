from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

# Start keyboard


def start_kb():
    playlist = KeyboardButton("Merge playlist")
    link = KeyboardButton("Merge links")
    keyboard = ReplyKeyboardMarkup(
        resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(playlist, link)
    return keyboard


def back_kb():
    back = KeyboardButton("Back")
    keyboard = ReplyKeyboardMarkup(
        resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(back)
    return keyboard


def pay_kb():
    keyboard = InlineKeyboardMarkup(row_width=1)
    yes = InlineKeyboardButton("Yes", callback_data="pay")
    no = InlineKeyboardButton("No", callback_data="no_pay")
    keyboard.add(yes, no)
    return keyboard


def chek_kb(isUrl=True, url="", bill=""):
    payMenu = InlineKeyboardMarkup(row_width=2)
    if isUrl:
        btnUrlQiwi = InlineKeyboardButton("Pay", url=url)
        payMenu.add(btnUrlQiwi)
    chek_pay = InlineKeyboardButton(
        "Check payment", callback_data="chek_"+bill)
    quit = InlineKeyboardButton("Quit", callback_data="quit")
    payMenu.insert(chek_pay).add(quit)
    return payMenu
