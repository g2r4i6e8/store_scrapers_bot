import os
import zipfile
from datetime import datetime
import logging
from zipfile import ZipFile

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
import re
from aiogram.types import ContentType
import shutil

from app.handlers.general import cmd_idle
from app.scrapers.lenta import parse_lenta
from app.scrapers.maxidom import parse_maxidom
from app.scrapers.poryadok import parse_poryadok
from app.scrapers.ulybka import parse_ulybka
from app.tools.clean_output import cleaner

logger = logging.getLogger(__name__)


class UserChoice(StatesGroup):
    waiting_for_store = State()
    waiting_for_link = State()

async def inquiry_start(message: types.Message, state: FSMContext):
    buttons = [["Лента"],
               # ["Hoff"],
               ["Максидом"],
               ["Порядок"],
               ['Улыбка радуги']]
    keyboard = types.ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=True)
    await message.answer("Для запуска сбора данных выбери магазин, используя клавиатуру ниже", reply_markup=keyboard)
    await UserChoice.waiting_for_store.set()

async def store_choice(message: types.Message, state: FSMContext):
    if message.content_type != ContentType.TEXT or message.text not in ['Лента', 'Hoff', 'Максидом', 'Порядок', 'Улыбка радуги']:
        await message.answer("Ошибочка\\. Пожалуйста, выбери магазин, используя клавиатуру ниже")
        return None

    chosen_store = message.text
    await state.update_data(chosen_store=chosen_store)

    link_text = "Теперь введи ссылку на раздел в выбранном магазине\n\nДопустимые форматы ввода:\n" \
                "https://lenta.com/catalog/bytovaya-himiya/sredstva-dlya-mytya-posudy/\n" \
                "https://www.r-ulybka.ru/u-catalog/vsye-dlya-doma/dlya-aromatizatsii/osvezhiteli-vozdukha/\n" \
                "https://www.maxidom.ru/catalog/osvezhiteli-vozduha/\n" \
                "https://spb.poryadok.ru/catalog/osvezhiteli_vozdukha/"
    await message.answer(link_text)

    await UserChoice.waiting_for_link.set()


async def link_set(message: types.Message, state: FSMContext):
    link_pattern = re.compile('(http|https):\/\/([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-])')
    if message.content_type != ContentType.TEXT:
        await message.answer("Ошибка 🙆‍♂️\n\nВведенный текст не похож на ссылку\\.")
        return None
    else:
        link = message.text
        await state.update_data(link=link)
        waiting_text = "Запрос принят в работу.\nСбор данных может занять некоторое время " \
                       "в зависимости от количества товаров в каталоге.\n\n" \
                       "В любом случае бот отпишется о результатах. " \
                       "А пока робот работает можно выпить чаю ☕ или напомнить близким о своей любви! ❤️"
        await message.answer(waiting_text)

    user_data = await state.get_data()
    try:
        if user_data['chosen_store'] == 'Лента':
            result = parse_lenta(user_data['link'], message.from_user.id)
        elif user_data['chosen_store'] == 'Максидом':
            result = parse_maxidom(user_data['link'], message.from_user.id)
        elif user_data['chosen_store'] == 'Порядок':
            result = parse_poryadok(user_data['link'], message.from_user.id)
        elif user_data['chosen_store'] == 'Улыбка радуги':
            result = parse_ulybka(user_data['link'], message.from_user.id)

        # elif user_data['chosen_store'] == 'Hoff':
        #     pass
            # output_path = parse_hoff(user_data['link'], path)

        output_path = shutil.make_archive(result, 'zip', result)
        await types.ChatActions.upload_document()
        caption_text = "Готово! Собранные данные ждут тебя в едином архиве\n\n" \
                       "P.S. Инструкцию по добавлению картинок в Excel можно скачать тут: google.com"
        await message.answer_document(open(output_path, 'rb'), caption=caption_text)
        await cleaner('data_{}'.format(message.from_user.id))
    except:
        await cleaner('data_{}'.format(message.from_user.id))
        await message.answer("В процессе сбора данных произошла ошибка 😢.\nПопробуй повторить запрос позже.")

    await cmd_idle(message, state)



def register_handlers_inquiry(dp: Dispatcher):
    dp.register_message_handler(inquiry_start, Text(equals="Начать работу"), state="*")
    dp.register_message_handler(inquiry_start, Text(equals="Продолжить работу"), state="*")
    dp.register_message_handler(store_choice, content_types=ContentType.ANY, state=UserChoice.waiting_for_store)
    dp.register_message_handler(link_set, content_types=ContentType.ANY, state=UserChoice.waiting_for_link)
