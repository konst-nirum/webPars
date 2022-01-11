from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from config import templates
import re


def mkeyboard(*args):
    res = ReplyKeyboardMarkup(resize_keyboard=True)
    for row in args:
        res.row(*[KeyboardButton(button) for button in row])
    return res


def isurl(text):
    return re.fullmatch(r'(http(s?)://)?t\.me.+', text)


def ikeyboard(*args):
    res = InlineKeyboardMarkup()
    for row in args:
        res.row(*[InlineKeyboardButton(button, callback_data=str(data)) if not isurl(data) else
                  InlineKeyboardButton(button, url=str(data)) for button, data in row])
    return res


keyboards = {'cancel': ikeyboard([('Отмена', 'cancel')])}


def addKeyboard(name):
    keyboard = templates['keyboards'][name]
    keyboard_buttons = {}
    if keyboard['type'] == 'keyboard':
        buttons = []
        for row in keyboard['buttons']:
            buttons.append([])
            for button in row:
                buttons[-1].append(button[0])
                keyboard_buttons[button[1]] = button[0].lower()
        keyboards[name] = mkeyboard(*buttons)
    if keyboard['type'] == 'ikeyboard':
        buttons = []
        for row in keyboard['buttons']:
            buttons.append([])
            for button in row:
                buttons[-1].append(tuple(button))
                keyboard_buttons[button[1]] = button[0].lower()
        keyboards[name] = keyboard(*buttons)
    return keyboard_buttons


menu_keyboard = addKeyboard('menu')
