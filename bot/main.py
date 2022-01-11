# -*- coding: utf-8 -*-
from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.exceptions import MessageCantBeDeleted, MessageToDeleteNotFound, MessageCantBeEdited, MessageToEditNotFound
from aiogram.types import InputMediaPhoto
from data.keyboards import keyboards, ikeyboard, menu_keyboard
from database import *
import pymorphy2, asyncio, re, json, requests, base64

morph = pymorphy2.MorphAnalyzer()

bot = Bot(token=token, parse_mode='HTML')
try:
    loop = asyncio.new_event_loop()
except RuntimeError:
    loop = asyncio.get_event_loop()
dp = Dispatcher(bot, loop=loop)


async def help_message(user_id):
    return await bot.send_message(user_id, templates['help']['desc'])


@dp.message_handler(commands=["help"])
async def help_handler(message: types.Message):
    return await help_message(message.from_user.id)


@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    from_user = message.from_user
    user_id, username, full_name = from_user.id, from_user.username, from_user.full_name
    status, user = User.add(user_id, username, full_name)
    if status == 'start':
        return await message.answer(templates['start'], reply_markup=keyboards['menu'])
    if user.scene != 'menu':
        User.edit(user, scene='menu')
    return await message.answer(templates['menu'], reply_markup=keyboards['menu'])


@dp.callback_query_handler()
async def callback(callback_query: types.CallbackQuery):
    message, text = callback_query.message, callback_query.data
    user_id, username, full_name = callback_query.from_user.id, callback_query.from_user.username, callback_query.from_user.full_name
    user = User.get(user_id)
    if user is None:
        user = User.add(user_id, username, full_name)
    if text == 'close':
        return await message.delete()


@dp.message_handler(content_types=['text'])
async def get_text(message: types.Message):
    if message.via_bot and message.via_bot.username == 'chememe_bot':
        return await message.reply(templates['oh_this_mine'])
    text, html_text, user_id = message.text.strip(), message.html_text, message.from_user.id
    command = text.lower()
    if not user_id:
        return
    user = User.get(user_id)
    if user is None:
        return await message.answer(templates['restart'])

    if command == menu_keyboard['help']:
        return await help_message(user_id)
    if command == menu_keyboard['settings']:
        return await message.answer(templates['developing'])
    if command == menu_keyboard['add']:
        User.edit(user, scene='site_add')
        return await message.answer(templates['site_add'])

    if user.scene == 'site_add':
        if not re.fullmatch('http(s)?://[^\n]+\n[^\n]+(\n[^\n]+)?', text):
            return await message.answer(templates['format'])
        regex = re.findall('(http(s)?://[^\n]+)\n([^\n]+)(\n([^\n]+))?', text)[0]
        url, css_path, js = regex[0], regex[2], bool(regex[4])
        User.edit(user, False, scene='start')
        site = Site.add(url, css_path, js)
        return await message.answer(templates['success_add'] % site.name)
    if text.startswith('/'):
        return await message.reply(templates['wCommand'])
    return await message.reply(templates['wMessage'])


if __name__ == '__main__':
    print("Bot successfully launched")
    executor.start_polling(dp)
