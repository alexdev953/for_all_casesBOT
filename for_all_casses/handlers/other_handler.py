from loader import dp
from aiogram import types


@dp.message_handler(content_types=['text'])
async def take_text(message: types.Message):
    if message.text.startswith('/'):
        await message.reply('Перевірьте чи правильно введена команда')
    else:
        await message.reply('Нажаль я ще не все вмію')
