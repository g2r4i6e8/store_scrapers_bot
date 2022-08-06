import logging
import os

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text, IDFilter

from app.tools.clean_output import cleaner

logger = logging.getLogger(__name__)


async def cmd_start(message: types.Message, state: FSMContext):
    await state.finish()
    logger.info(f"User {message.from_user.id} ({message.from_user.username}) started the bot instance")

    button = [["Начать работу"]]
    keyboard = types.ReplyKeyboardMarkup(button, resize_keyboard=True, one_time_keyboard=True)
    welcome_text = "Привет 👐\n\nБот создан для конкурентного анализа рынков\n\n" \
                   "NB\\! Продукт представлен как есть \\(as is\\)\\. " \
                   "Поддержка работоспособности бота выполняется разработчиком в свободное время " \
                   "\n\nРазработчик\\: @akolomatskiy"
    await message.answer(welcome_text,
                         reply_markup=keyboard,
                         parse_mode="MarkdownV2")


async def cmd_idle(message: types.Message, state: FSMContext):
    await state.finish()
    await cleaner('data_{}'.format(message.from_user.id))
    button = [["Продолжить работу"],
              ["Поддержать проект"]]
    keyboard = types.ReplyKeyboardMarkup(button, resize_keyboard=True, one_time_keyboard=True)
    idle_text = "Продолжим сбор данных\\?\n\n" \
                "P\\. S\\. Если бот был полезен, ты всегда можешь отблагодарить разработчика через кнопку " \
                "\"Поддержать проект\""
    await message.answer(idle_text,
                         reply_markup=keyboard,
                         parse_mode="MarkdownV2")


async def cmd_donate(message: types.Message, state: FSMContext):
    await state.finish()

    inline_kb = types.InlineKeyboardMarkup()
    donate_text = "Привет! Меня зовут Андрей Коломацкий и я - разработчик этого бота.\n\n" \
                  "Для стабильной работы бота требуется оплата серверов, работающих 24/7." \
                  "Если тебе нравится моя работа, нажми на кнопку 'Поддержать проект' и переведи " \
                  "любую сумму на мой счет.\n\nСпасибо! 🙏"
    inline_kb.row(types.InlineKeyboardButton("Поддержать проект",
                                             url='https://yoomoney.ru/to/4100117228897097'))

    await message.answer(donate_text, reply_markup=inline_kb)

    await cmd_idle(message, state)

async def cmd_help(message: types.Message, state: FSMContext):
    await state.finish()
    await cleaner('data_{}'.format(message.from_user.id))
    help_text = "Нужна помощь или хочешь оставить обратную свзяь? Пиши @akolomatskiy." \
                "\n\nЧтобы открыть меню нажми /idle."
    await message.answer(help_text)


# Просто функция, которая доступна только администратору,
# чей ID указан в файле конфигурации.
async def secret_command(message: types.Message):
    await message.answer("Поздравляю! Эта команда доступна только администратору бота.")


def register_handlers_common(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands="start", state="*")
    dp.register_message_handler(cmd_donate, commands="donate", state="*")
    dp.register_message_handler(cmd_donate, Text(equals="Поддержать проект"))
    dp.register_message_handler(cmd_help, commands="help", state="*")
    dp.register_message_handler(cmd_idle, commands="idle", state="*")
