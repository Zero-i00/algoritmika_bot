import os
import aiogram.utils.markdown as md
from aiogram.dispatcher import FSMContext
from aiogram.utils import executor
from aiogram import Bot, types, Dispatcher
from dotenv import load_dotenv
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup, message

load_dotenv()
from aiogram.dispatcher.filters import Text, state
from aiogram.types import ParseMode

bot = Bot(token=os.environ.get('TOKEN'), parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class Form(StatesGroup):
    name = State()
    age = State()
    gender = State()
    hobby = State()
    invalid = State()


@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await Form.name.set()
    await message.reply('''Здравствуйте, этот бот создан
для того чтобы помочь найти вам команду.
Надеемся что у вас это получится
и опасайтесь мошенников.''')
    await message.reply("Укажите ваше ФИО")


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
    await message.reply("Напишите немного о себе")


@dp.message_handler(state=Form.hobby)
async def process_gender(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['hobby'] = message.text
        keyboard = InlineKeyboardMarkup()
        inline_btn_1 = InlineKeyboardButton('Оставить', callback_data='button2')
        keyboard.add(inline_btn_1)
        inline_btn_2 = InlineKeyboardButton('Удалить', callback_data='button1')
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


@dp.callback_query_handler(lambda c: c.data == 'button1')
async def process_callback_button1(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Отмена')
@dp.callback_query_handler(lambda c: c.data == 'button2')
async def process_callback_button1(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Сохранить')

def main():
    executor.start_polling(dp)


if __name__ == '__main__':
    main()
