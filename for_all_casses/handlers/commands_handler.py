from aiogram import types
from for_all_casses import db
from for_all_casses.utilities import markup, help_user, CheckIMEI, check_imt
from loader import dp, bot

check_imei = CheckIMEI()


@dp.message_handler(commands=['start', 'help', 'imt', 'toadmin', 'imei'])
async def take_command_user(message: types.Message):
    db.last_uses(message.from_user.id)
    if message.text == '/start':
        about_bot = await bot.get_me()
        db.check_user(message.chat.id, message.from_user.first_name, message.from_user.username)
        await message.answer(
            f"Привіт, {message.from_user.first_name}!\nЯ - <b>{about_bot['first_name']}</b> бот створений "
            f"на всі випадки життя.\n\n{help_user()}", reply_markup=markup)
    elif message.text == '/help':
        await message.answer(f"Допомога користувачу 👇\n\n{help_user()}")
    elif message.text.startswith('/imt'):
        clear_imt = message.text[5:]
        if not clear_imt:
            await message.answer('Ви нічого не ввели, введіть дані у форматі '
                                 'Вага(КГ,Г) Зріст(М,СМ) наприклад /imt 80,0 1,75')
        else:
            msg = check_imt(clear_imt)
            await message.answer(msg)
    elif message.text.startswith('/toadmin') and len(message.text.split()) > 1:
        await bot.send_message(379210271,
                               f"<b>Від:</b> {message.from_user.first_name} {message.from_user.id}\n"
                               f"<b>Текст повідомлення:</b>\n{message.text.replace('/toadmin ', '').capitalize()}",
                               reply_markup=markup)
    elif message.text.startswith('/imei'):
        clear_imei = message.text[6:]
        if len(clear_imei) < 8:
            await message.answer('Перевірте чи правильно введений IMEI', reply_markup=markup)
        else:
            msg = check_imei.web_check_imei(clear_imei)
            await message.answer(msg, reply_markup=markup)
