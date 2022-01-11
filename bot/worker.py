# -*- coding: utf-8 -*-
from aiogram import Bot, Dispatcher
from data.keyboards import keyboards
from database import *
import asyncio, time, json

bot = Bot(token=token, parse_mode='HTML')
loop = asyncio.new_event_loop()
dp = Dispatcher(bot, loop=loop)


def title_msg(title):
    return f"<b>Новое уведомление!</b>\n\n<a href='{title['url']}'><b>{title['name']}</b></a>\n{title['title']}"


async def get_new_posts():
    time_now = now()
    updating_sites = Site.get_updating()
    new_titles = []
    for site in updating_sites:
        title = get_title(site.url, site.css_path, site.js_required)
        title_hash = get_hash(title)
        if title is None or title_hash == site.title_hash:
            continue
        site.update_time = time_now
        site.title_hash = title_hash
        new_titles.append({'name': site.name, 'url': site.url, 'title': title})
        if site.translate:
            new_titles[-1]['title'] = translate(title)

    if len(new_titles):
        session.commit()

    subscribers = User.subscribed()
    for user in subscribers:
        for title in new_titles:
            await bot.send_message(user.user_id, title_msg(title), disable_web_page_preview=True)
            await asyncio.sleep(0.1)


async def worker():
    while True:
        await get_new_posts()
        time.sleep(5)


if __name__ == '__main__':
    print('Worker successfully launched')
    asyncio.run(worker())
