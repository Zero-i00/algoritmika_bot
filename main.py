import os

from aiogram.dispatcher.filters import Text
from aiogram.utils import executor
from aiogram import Bot, types, Dispatcher
from dotenv import load_dotenv

load_dotenv()

bot = Bot(token=os.environ.get('TOKEN'), parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    start_buttons = ['Помощь', 'Найти команду']
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(*start_buttons)
    await message.answer('Ку огузок', reply_markup=keyboard)


@dp.message_handler(Text(equals='Помощь'))
async def get_phones(message: types.Message):
    await message.answer('''Помощь: 
    Что может этот бот?
    Он может помоч вам нати команду.
    Как её найти?
    Чтобы её найти надо нажать на кнопку  найти команду.''')


@dp.message_handler(Text(equals='Найти команду'))
async def get_phones(message: types.Message):
    await message.answer('''Когда бот найдет подходящюю команду для вас он вам напишет
''')



def main():
    executor.start_polling(dp)


if __name__ == '__main__':
    main()
