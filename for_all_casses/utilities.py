from aiogram import types
from bs4 import BeautifulSoup
import psycopg2
import logging
from bot_config import *
from pytube import YouTube
import ffmpeg
from eyed3.id3 import Tag
import requests
from loader import owm, bot
import urllib.request

logger = logging.getLogger('utilities')

markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
markup.add('🤭 Insta_grabber', '📺 YouTube Music (beta)')
markup.add('🎲 Випадкове число', '🤖 Ваш chat_id', '🌤 Погода')
markup.add('📊 Курс Валют на сьогодні')


# Функція для видалення поганих символів з назви(пісні, відео)
def good_name(name: str) -> str:
    list_with_bad_symbols = list('*.?,:/|$')
    for symbols in list_with_bad_symbols:

        name = name.replace(symbols, '')
    return name


def weather_in_city(city: str) -> str:
    try:
        observation = owm.weather_at_place(city)
        w = observation.get_weather()
        h = w.get_humidity()
        t = w.get_temperature('celsius')["temp"]
        wind = w.get_wind()["speed"]
        answer_msg = f"В {city} зараз: \n{w.get_detailed_status()} \n💦 Вологість : {h}\n🌡 Температура :" \
                     f" {t}\n🎏 Швидкість вітру: {wind} м/с"
        return answer_msg
    except Exception:
        return 'Щось пішло не так 🙈'


def yt_download(message_url: str):
    logger.debug(message_url)
    try:
        yt = YouTube(message_url)
        name_music = yt.title
        length_video_min = yt.length // 60
        while name_music == 'YouTube':
            yt = YouTube(message_url)
            name_music = yt.title
            length_video_min = yt.length // 60
        if length_video_min >= 16:
            return 'Error length'
        preview_thumb = jpeg_download(yt.thumbnail_url, name_music)
        name_music = f"{good_name(yt.title)}.mp4"
        yt.streams.get_audio_only().download(output_path=f"/home/apache/servers/SMB/downloads/music_bot/yt_video/")
        dwn_dir = f'/home/apache/servers/SMB/downloads/music_bot/{name_music.replace(".mp4", ".mp3")}'
        logger.info(dwn_dir)
        logger.info(name_music)
        (
            ffmpeg
                .input(f"/home/apache/servers/SMB/downloads/music_bot/yt_video/{name_music}")
                .output(f'{dwn_dir}', **{'qscale:a': 1})
                .overwrite_output()
                .run()
        )
    except Exception as error:
        logger.error(f"Error in yt_download{error}")
        return 'Error download'
    return dwn_dir, name_music, preview_thumb


def jpeg_download(url, jpeg_name):
    jpeg_path = f"/home/apache/servers/SMB/downloads/music_bot/yt_video/THUMBS/{jpeg_name}.jpg"
    urllib.request.urlretrieve(url, jpeg_path)
    return jpeg_path


def music_naming(path_to_file, music_performer, music_title):
    logger.info(path_to_file)
    audiofile = Tag()
    logger.info(audiofile)
    audiofile.parse(path_to_file)
    audiofile.artist = f"{music_performer}"
    audiofile.title = f"{music_title}"
    audiofile.save()
    logger.info(f'New audio attribute: Artist: {audiofile.artist}, Title: {audiofile.title}')


async def download_music(file):
    file_id = file.file_id
    file_get = await bot.get_file(file_id=file_id)
    file_path = file_get.file_path
    music_performer = good_name(file.performer)
    music_title = good_name(file.title)
    download_path = f'/home/apache/servers/SMB/downloads/music_bot/renameToBot/' \
                    f'{music_performer} - {music_title}.mp3'
    await bot.download_file(file_path, download_path)
    try:
        music_naming(download_path, music_performer, music_title)
    except Exception as e:
        logger.error(f'Error in music_naming: {e}')
    return download_path


def help_user():
    answer = 'Даний бот має дещо цікаве для тебе, знизу є клавіатура з доступними функціями.\n' \
             '⚪️ Для опрацювання відео з Youtube натисніть (📺 YouTube Music),' \
             ' після цього вставте посилання на відео з якого ' \
             'потрібно стягнути аудіо.\n⚪️ Для стягнення фото або відео ' \
             'з Instagram натисніть (🤭 Insta_grabber) та вставте ' \
             'посилання (Профіль звідки буде стягуватися фото або відео повинен бути відкритим 🙊)\n' \
             '⚪️ Також я можу змінити назву виконавця пісні на ту яку ви попросите (буде цікаве тим в кого є свій ' \
             'музичний канал або група), щоб це зробити напиши мені використовуючи /toadmin ТЕКСТ звернення\n' \
             '⚪️ Кнопка (🎲 Випадкове число) повертає випадкове число від 0 до 100\n' \
             '⚪️ Для того щоб розрахувати ваш ІМТ (Індекс маси тіла) введіть команду /imt у форматі ' \
             'Вага(КГ,Г) Зріст(М,СМ)\n<b>Наприклад:</b> /imt 80,0 1,75\n' \
             '⚪️ Для пошуку моделі телефона використовуйте команду /imei IMEI телефона\n' \
             '<b>Наприклад:</b> /imei 12345678912345'

    return answer


class CheckIMEI:

    def __init__(self):
        self.headers = {"authority": "xinit.ru",
                        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                                      "(KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36",
                        "accept": "*/*",
                        "sec-fetch-site": "same-origin",
                        "sec-fetch-mode": "sec-fetch-mode",
                        "sec-fetch-dest": "sec-fetch-dest",
                        "referer": "https://xinit.ru/imei/",
                        "accept-language": "uk,ru-RU;q=0.9,ru;q=0.8,en-US;q=0.7,en;q=0.6",
                        "cookie": "_ga=GA1.2.1458043199.1587534621; _gid=GA1.2.1008845724.1593671486"}

    def web_check_imei(self, imei):
        """
        Ф-ція перевірки IMEI на сайті
        :param imei:
        :return:
        """
        info_imei_list = []
        info_imei_atr = []
        url_base = f'https://xinit.ru/api/imei/{imei}'
        # Check valid cert
        try:
            response = requests.get(url_base, headers=self.headers)
        except requests.exceptions.SSLError:
            logger.warning(f'Поганий сертифікат для сайта: {url_base}')
            response = requests.get(url_base, headers=self.headers, verify=False)

        # TODO Передивитися даний if (можливо можна зробити іншу перевірку)
        if response.json() is None or len(response.json()) == 1:
            return f'<b>IMEI: </b>{self.imei_check_num(imei[0:14])} не знайдено 😥'
        else:

            for values in response.json()[1:4]:
                info_imei_atr.append(values['info'])
                info_imei_list.append(f"📱 {values['info']}")
            str_to_bot = '\n\n'.join(info_imei_list)
            return f"<b>Мобільний телефон:</b>\n<b>IMEI: </b>{self.imei_check_num(imei[0:14])}\n\n{str_to_bot}"

    @staticmethod
    def imei_check_num(imei: str) -> str:
        """Функція розрахунку останньої цифри в IMEI"""
        imei_l = list(imei)
        sum_second = 0
        check_numb = 0
        for second_val in imei_l[1::2]:
            sum_second1 = int(second_val) + int(second_val)
            if len(str(sum_second1)) == 2:
                sum_second1 = int(str(sum_second1)[0]) + int(str(sum_second1)[1])
            sum_second += sum_second1
        for first_val in imei_l[0::2]:
            sum_second += int(first_val)
        while sum_second % 10 != 0:
            for check_sum in range(10):
                find_check_sum = sum_second
                checking_sum = find_check_sum + check_sum
                if checking_sum % 10 == 0:
                    sum_second += check_sum
                    check_numb = check_sum
        return f"{imei}{check_numb}"


def check_imt(imt):
    good_str = imt.replace(',', '.').split()
    try:
        imt_kg = float(good_str[0])
        imt_m = float(good_str[1])
    except TypeError:
        return "Сталася помилка, Дані введено не правильно!!! " \
               "Введіть дані у форматі Вага(КГ,Г) Зріст(М,СМ) наприклад /imt 80,0 1,75"
    imt_result = round(imt_kg / (imt_m ** 2), 2)
    imt_info = None
    if imt_result < 18.5:
        imt_info = 'недостатня вага🤭'
    elif 18.6 < imt_result < 24.9:
        imt_info = 'нормальна вага😃'
    elif 25 < imt_result < 29.9:
        imt_info = 'передожиріння (Гладкість)🤫'
    elif 30 < imt_result < 34.9:
        imt_info = 'ожиріння I ступеня😬'
    elif 35 < imt_result < 39.9:
        imt_info = 'ожиріння II ступеня😨'
    elif imt_result > 40:
        imt_info = 'ожиріння III ступеня😱'
    return f'Ваш ІМТ: {imt_result}\nУ вас {imt_info}'


def check_curency():
    """Функція перевірки курсу валют на сьогодні"""
    page = requests.get(URL_CURRENCY)
    if page:
        list_currency = []
        soup = BeautifulSoup(page.text, "html.parser")
        spans = soup.find(class_='widget-currency_cash').find_all('span')
        for span in spans:
            list_currency.append(span.text)

        def format_currency(currency):
            return str(round(float(currency), 2))

        format_USD = f'💵USD:\n<b>Купівля:</b> {format_currency(list_currency[1])}\n' \
                     f'<b>Продаж:</b> {format_currency(list_currency[4])}'
        format_EUR = f'💶EUR:\n<b>Купівля:</b> {format_currency(list_currency[7])}\n' \
                     f'<b>Продаж:</b> {format_currency(list_currency[10])}'
        return f'{format_USD}\n{format_EUR}'


def insta_grabber(url_msg: str) -> str:
    parse_url = url_msg.split('/')
    if len(parse_url) <= 1:
        return 'Посилання не вірне'
    good_url = f'https://{parse_url[2]}/{parse_url[3]}/{parse_url[4]}?__a=1'
    page = requests.get(good_url)
    if page:
        take_json = page.json()['graphql']['shortcode_media']
        if take_json['__typename'] == 'GraphVideo':
            video = take_json['video_url']
            return f'<a href="{video}">Відео</a>'
        elif take_json['__typename'] == 'GraphImage':
            photo = take_json['display_url']
            return f'<a href="{photo}">Фото</a>'


class DbFunction:
    @staticmethod
    def db_connect(sql, values=None):
        con = None
        try:
            con = psycopg2.connect(database=FOR_ALL_CASES_DB, user=FOR_ALL_CASES_USER, password=FOR_ALL_CASES_PWD,
                                   host=FOR_ALL_CASES_HOST, port=FOR_ALL_CASES_PORT)
            con.autocommit = True
            cur = con.cursor()
            if values:
                cur.execute(sql, values)
            else:
                cur.execute(sql)
            output = cur.fetchall()
            cur.close()
            return output
        except psycopg2.Error as error:
            logger.error(f"Помилка в базі: {error}")
            return False
        finally:
            if con is not None:
                con.close()

    def last_uses(self, id_user):
        self.db_connect("update users set last_uses = now() where chat_id = %s returning last_uses", (id_user,))

    def check_admin(self, id_user):
        info = self.db_connect("select admin from users where chat_id = %s and admin ='1'", (id_user,))
        for values in info:
            if values:
                return True

    def check_user(self, user_id, first_name, user_name):
        logger.debug(f'Check USER {user_id}, {first_name}, {user_name}')
        info = self.db_connect("select chat_id from users where chat_id = %s", (user_id,))
        if not info:
            self.db_connect("insert into users (chat_id, tg_name, tg_user_name) values (%s, %s, %s) returning id",
                            (user_id, first_name, user_name,))

    def all_chat_id(self) -> list:
        return self.db_connect("select chat_id from users")

    def db_check_performer(self, id_user: str) -> bool:
        info = self.db_connect("select user_performer from users us "
                               "inner join performer_tbl pt on pt.performer_id = us.performer_id where chat_id = %s",
                               (id_user,))
        logger.debug(f'Check_performer: {info}')
        for values in info[0]:
            if values:
                return True
            else:
                return False

    def db_get_performer(self, id_user: str) -> tuple:
        info = self.db_connect("select user_performer, thumb_path from users us "
                               "inner join performer_tbl pt on pt.performer_id = us.performer_id where chat_id = %s",
                               (id_user,))
        logger.debug(f'Get_performer and thumb: {info}')
        for performer, thumb in info:
            return performer, thumb
