from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from bot_config import TOKEN_BOT, TOKEN_OWM
import pyowm
import logging

# Init logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)  # TODO before commit check log level
console_log = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_log.setFormatter(formatter)
logger.addHandler(console_log)


# Init bot and DP
bot = Bot(token=TOKEN_BOT, parse_mode=types.ParseMode.HTML)
memory_storage = MemoryStorage()
dp = Dispatcher(bot, storage=memory_storage)

# open weather channel
owm = pyowm.OWM(TOKEN_OWM, language='ua')