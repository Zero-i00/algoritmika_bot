import os
import aiogram.utils.markdown as md
from aiogram.dispatcher import FSMContext
from aiogram.utils import executor
from aiogram import Bot, types, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from aiogram.dispatcher.filters import Text
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class RedirectMessageType:
    title: str
    description: str


bot = Bot(token=os.environ.get('TOKEN'), parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class Form(StatesGroup):
    name = State()
    age = State()
    gender = State()
    hobby = State()


# @dp.message_handler(state='*', commands='cancel')
# @dp.message_handler(commands=['start'])
# async def cmd_start(message: types.Message):
#     await Form.name.set()
#     await message.reply("Укажите ваше ФИО")


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    start_buttons = ['Помощь', 'Найти команду', 'Моё резюме']
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(*start_buttons)
    await message.reply('''
Здравствуйте, этот бот создан
для того, чтобы помочь найти вам команду.
Надеемся, что у вас это получится.''', reply_markup=keyboard)


@dp.message_handler(Text(equals='Помощь'))
async def get_phones(message: types.Message):
    await message.answer('''Помощь: 
    Что может этот бот?
    Он может помочь вам найти команду.
    Как её найти?
    Чтобы её найти, надо нажать на кнопку "Найти команду".''')


@dp.message_handler(Text(equals='Найти команду'))
async def get_phones(message: types.Message):
    await message.answer('''Когда бот найдет подходящюю команду для вас, он вам напишет!!!
''')


@dp.message_handler(Text(equals='Моё резюме'))
async def get_phones(message: types.Message):
    await Form.name.set()
    await message.reply("Укажите ваше ФИО")


def handle_redirect(text: str) -> RedirectMessageType | None:
    processed: str = text.lower()

    match processed:
        case 'помощь':
            return RedirectMessageType(
                title="помощь",
                description="Нажмите накнопку, чтобы перейти к боту"
            )
        case "найти команду":
            return RedirectMessageType(
                title="Поиск команды",
                description="Нажмите накнопку, чтобы перейти к боту"
            )
        case "моё":
            return RedirectMessageType(
                title="Редактировать моё ризюме",
                description="Нажмите накнопку чтобы перейти к боту"
            )
        case _:
            return


@dp.message_handler()
async def handle_message(message: types.Message) -> None:
    message_type = message.chat.type
    text: str = message.text

    keyboard = InlineKeyboardMarkup()
    bot_chat = f'tg://resolve?domain={os.environ.get("BOT_USERNAME").replace("@", "")}&start=chat'

    if message_type == 'supergroup' and os.environ.get("BOT_USERNAME") in text:
        new_text: str = text.replace(os.environ.get("BOT_USERNAME"), '').strip()
        response = handle_redirect(new_text)
        if response:
            url_button = InlineKeyboardButton(text=response.title, url=bot_chat)
            keyboard.add(url_button)

            await message.reply(
                text=response.description,
                reply_markup=keyboard
            )


@dp.message_handler(state=Form.name)
async def process_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
    await Form.next()
    await message.reply("Сколько вам лет?")


@dp.message_handler(lambda message: not message.text.isdigit(), state=Form.age)
async def process_age_invalid(message: types.Message):
    return await message.reply("Это не число!")


# Принимаем возраст и узнаём пол
@dp.message_handler(lambda message: message.text.isdigit(), state=Form.age)
async def process_age(message: types.Message, state: FSMContext):
    await Form.next()
    await state.update_data(age=int(message.text))
    await message.reply("Каковы ваши основные достоинства?")


@dp.message_handler(state=Form.gender)
async def process_gender(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['gender'] = message.text
    await Form.next()
    await message.reply("Расскажите немного о себе")


@dp.message_handler(state=Form.hobby)
async def process_gender(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['hobby'] = message.text
        keyboard = InlineKeyboardMarkup()
        inline_btn_1 = InlineKeyboardButton('Сохранить', callback_data='button_resume_send')
        keyboard.add(inline_btn_1)
        inline_btn_2 = InlineKeyboardButton('Удалить', callback_data='button_resume_cancel')
        keyboard.add(inline_btn_2)
        await message.answer(
            md.text(
                md.text('ФИО:', md.bold(data['name'])),
                md.text('Возраст:', md.code(data['age'])),
                md.text('Достоинства:', data['gender']),
                md.text('О себе:', md.bold(data['hobby'])),
                sep='\n',
            ),
            reply_markup=keyboard
        )
    await state.finish()


@dp.callback_query_handler(lambda c: c.data == 'button_resume_cancel')
async def process_callback_button1(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Отмена')


@dp.callback_query_handler(lambda c: c.data == 'button_resume_send')
async def process_callback_button1(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Сохранить')


def main():
    executor.start_polling(dp)


if __name__ == '__main__':
    main()
