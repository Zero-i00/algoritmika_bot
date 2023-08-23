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


class TeamForm(StatesGroup):
    team_description = State()


class ResumeForm(StatesGroup):
    name = State()
    age = State()
    gender = State()
    hobby = State()


bot = Bot(token=os.environ.get('TOKEN'), parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


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
async def help_handler(message: types.Message):
    await message.answer('''Помощь: 
    Что может этот бот?
    Он может помочь вам найти команду.
    Как её найти?
    Чтобы её найти, надо нажать на кнопку "Найти команду".''')


@dp.message_handler(Text(equals='Найти команду'))
async def find_team_handler(message: types.Message):
    await TeamForm.team_description.set()
    await message.answer('Опиши свои идеи, для чего вам нужна команда.')


@dp.message_handler(Text(equals='Моё резюме'))
async def get_phones(message: types.Message):
    await ResumeForm.name.set()
    await message.reply("Укажите ваше ФИО")


def handle_redirect(text: str) -> RedirectMessageType | None:
    processed: str = text.lower()

    match processed:
        case 'помощь':
            return RedirectMessageType(
                title="помощь",
                description="Нажмите на кнопку, чтобы перейти к боту"
            )
        case "найти команду":
            return RedirectMessageType(
                title="Поиск команды",
                description="Нажмите на кнопку, чтобы перейти к боту"
            )
        case "моё":
            return RedirectMessageType(
                title="Редактировать моё ризюме",
                description="Нажмите на кнопку чтобы перейти к боту"
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


@dp.message_handler(state=ResumeForm.name)
async def process_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
    await ResumeForm.next()
    await message.reply("Сколько вам лет?")


@dp.message_handler(lambda message: not message.text.isdigit(), state=ResumeForm.age)
async def process_age_invalid(message: types.Message):
    return await message.reply("Это не число!")



@dp.message_handler(lambda message: message.text.isdigit(), state=ResumeForm.age)
async def process_age(message: types.Message, state: FSMContext):
    await ResumeForm.next()
    await state.update_data(age=int(message.text))
    await message.reply("Каковы ваши основные достоинства?")


@dp.message_handler(state=ResumeForm.gender)
async def process_gender(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['gender'] = message.text
    await ResumeForm.next()
    await message.reply("Напишите о себе")


@dp.message_handler(state=ResumeForm.hobby)
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
                md.text('Имя:', md.bold(data['name'])),
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

    
@dp.message_handler(state=TeamForm.team_description)
async def process_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['team_description'] = message.text
        keyboard = InlineKeyboardMarkup(row_width=2)
        button_send = InlineKeyboardButton(text="Отправить в группу", callback_data='button_send')
        button_cancel = InlineKeyboardButton(text="Не отправлять в группу", callback_data='button_cancel')
        keyboard.add(button_send).add(button_cancel)
        await message.answer(text=message.text, reply_markup=keyboard)
        await state.finish()


@dp.callback_query_handler()
async def vote_callback(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == 'button_send':
        async with state.proxy() as data:
            options = ["набор команды", "не интересно"]
            await bot.send_poll(chat_id=os.environ.get('CHAT_ID'),
                                question=data['team_description'],
                                options=options,
                                is_anonymous=False,
                                allows_multiple_answers=False)
    elif callback.data == 'button_cancel':
        await callback.answer(text='Хорошо')


def main():
    executor.start_polling(dp)


if __name__ == '__main__':
    main()
