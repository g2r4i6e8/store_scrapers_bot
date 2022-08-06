import asyncio
import logging
import os
import sqlite3
import sys

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from datetime import datetime

from app.config_reader import load_config
from app.handlers.inquiry import register_handlers_inquiry
from app.handlers.general import register_handlers_common

logger = logging.getLogger(__name__)

async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="/start", description="Начать"),
        BotCommand(command="/idle", description="Главное меню"),
        BotCommand(command="/donate", description="Поддержать проект"),
        BotCommand(command="/help", description="Помощь")
    ]
    await bot.set_my_commands(commands)


async def main():
    # setting up logging
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    os.makedirs('logs', exist_ok=True)
    logfile = 'logs/{}.log'.format(datetime.now().strftime("%Y-%m-%dT%H"))
    logging.basicConfig(
        stream=sys.stdout,
        # filename=logfile,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    logger = logging.getLogger(__name__)
    logger.info("Starting bot")

    # parsing config
    config = load_config(os.path.join('config', 'bot.ini'))

    os.environ['db_file'] = "db/database.db"

    # ininitalizing bot
    bot = Bot(token=config.tg_bot.token)
    dp = Dispatcher(bot, storage=MemoryStorage())


    # Регистрация хэндлеров
    register_handlers_common(dp)
    # register_handlers_abracadabra(dp, config.tg_bot.admin_id)
    register_handlers_inquiry(dp)

    # Установка команд бота
    await set_commands(bot)

    # Запуск поллинга
    # await dp.skip_updates()  # пропуск накопившихся апдейтов (необязательно)
    await dp.start_polling()


if __name__ == '__main__':
    asyncio.run(main())
