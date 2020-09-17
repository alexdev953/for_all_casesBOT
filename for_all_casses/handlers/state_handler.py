from aiogram.dispatcher import FSMContext
from aiogram import types
from aiogram.dispatcher.filters.state import State, StatesGroup
from loader import dp, bot
from ..utilities import markup, insta_grabber, yt_download, weather_in_city
from for_all_casses import db
import logging
from for_all_casses import loop

logger = logging.getLogger('state_handler')

# Inline Keyboard settings
keyboard_inline = types.InlineKeyboardMarkup(row_width=1)
keyboard_inline.add(types.InlineKeyboardButton('❌ Скасувати', callback_data=f'❌no'))


class NextStep(StatesGroup):
    waiting_for_city_name = State()
    waiting_for_insta_url = State()
    waiting_for_yt_url = State()


@dp.message_handler(text=['🌤 Погода', '🤭 Insta_grabber', '📺 YouTube Music (beta)'], state='*')
async def take_button(message: types.Message):
    db.last_uses(message.from_user.id)
    if message.text == '🌤 Погода':
        await message.answer("Введіть назву міста: ", reply_markup=keyboard_inline)
        await NextStep.waiting_for_city_name.set()
    elif message.text == '🤭 Insta_grabber':
        await message.answer('Вставте посилання на фото або відео', reply_markup=keyboard_inline)
        await NextStep.waiting_for_insta_url.set()
    elif message.text == '📺 YouTube Music (beta)':

        await message.answer('Вставте посилання на відео.\n Функція на стадії тестування 👨🏻‍💻',
                             reply_markup=keyboard_inline)
        await NextStep.waiting_for_yt_url.set()


@dp.message_handler(state=NextStep.waiting_for_city_name, content_types=types.ContentTypes.TEXT)
async def check_city(message: types.Message, state: FSMContext):
    answer_msg = weather_in_city(message.text)
    await state.finish()
    await message.answer(answer_msg, reply_markup=markup)


@dp.message_handler(state=NextStep.waiting_for_insta_url, content_types=types.ContentTypes.TEXT)
async def take_insta_url(message: types.Message, state: FSMContext):
    answer_msg = insta_grabber(message.text)
    await message.answer(answer_msg)
    await state.finish()


@dp.message_handler(state=NextStep.waiting_for_yt_url, content_types=types.ContentTypes.TEXT)
async def take_yt_url_2(message: types.Message, state: FSMContext):
    url = message.text
    await state.finish()
    if len(url.split('/')) > 1 and url.find('you') != -1:
        await message.answer('Твориться магія 💫 і відео перетворюється в музику',
                             disable_notification=True)
        music_url = await loop.run_in_executor(None, yt_download, url)
        logger.debug(f'MUSIC_URL{music_url}')
        if str(music_url) == 'Error download':
            await message.answer('Щось пішло не так 🙈, звернітся до адміністратора\n'
                                 '/toadmin текст звернення')
        elif str(music_url) == 'Error lenght':
            await message.answer('Відео довше 15 хвилин, нажаль це дуже довго 🤥')
        else:
            await bot.send_chat_action(message.from_user.id, 'upload_audio')
            await message.answer('Йде відправка аудіо 📤 ', disable_notification=True)
            await bot.send_audio(message.from_user.id, open(str(music_url[0]), 'rb'),
                                 title=music_url[1], thumb=open(music_url[2], 'rb'), reply_markup=markup)


@dp.callback_query_handler(text_startswith='❌no', state='*')
async def state_cancel(query: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await query.answer("Охрана отмєна 😎")
    await bot.edit_message_reply_markup(query.from_user.id, query.message.message_id)
