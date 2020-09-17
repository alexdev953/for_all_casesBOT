from aiogram import types, exceptions
from for_all_casses import db
from for_all_casses.utilities import markup
from loader import dp, bot


@dp.message_handler(lambda message: db.check_admin(message.chat.id), commands=['attention'])
async def take_attention(message: types.Message):
    db.last_uses(message.from_user.id)
    for values in db.all_chat_id():
        try:
            await bot.send_message(values[0], message.text.replace('/attention ', '').capitalize(), reply_markup=markup)
        except exceptions.ChatNotFound:
            continue


@dp.message_handler(lambda message: db.check_admin(message.chat.id), commands=['test'])
async def take_test(message: types.Message):
    await message.answer('Тест успішний ви адмін')