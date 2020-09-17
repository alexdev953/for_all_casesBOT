from loader import dp, bot
from random import randint
from aiogram import types
import logging
from for_all_casses.utilities import help_user, markup, check_curency, download_music
from for_all_casses import db
from bot_config import THUMB_PATH

logger = logging.getLogger('handler')


@dp.message_handler(
    text=['🎲 Випадкове число', '📊 Курс Валют на сьогодні', '🤖 Ваш chat_id', '🥇 ІМТ', '🆘 Інструкція'])
async def take_text(message: types.Message):
    db.last_uses(message.from_user.id)
    if message.text == '🎲 Випадкове число':
        await message.answer(str(randint(1, 100)))
    elif message.text == '📊 Курс Валют на сьогодні':
        msg = check_curency()
        await message.answer(msg, reply_markup=markup)
    elif message.text == '🤖 Ваш chat_id':
        await message.answer(message.chat.id)

    elif message.text == '🆘 Інструкція':
        await message.answer(help_user(), reply_markup=markup)


@dp.message_handler(lambda message: db.db_check_performer(message.from_user.id), content_types=['audio'])
async def take_forward(message: types.Message):
    file = message.audio
    logger.info(file)
    db.last_uses(message.from_user.id)
    performer, thumb_pic = db.db_get_performer(message.from_user.id)
    downloaded = await download_music(file=file)
    await message.answer('Обробка аудіо 🎼', disable_notification=True)
    await bot.send_chat_action(message.from_user.id, 'upload_audio')
    if downloaded:
        await bot.send_message(message.from_user.id, 'Вигружається в Telegram 📤', disable_notification=True)
        await bot.send_audio(message.from_user.id, open(str(downloaded), 'rb'), performer=f'{performer}',
                             title=f'{message.audio.performer} - {message.audio.title}',
                             reply_markup=markup,
                             thumb=open(thumb_pic, 'rb'))
    else:
        await message.answer('Сталася помилка')
