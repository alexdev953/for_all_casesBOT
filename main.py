from aiogram import executor
from loader import dp, logger
import for_all_casses.handlers

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
