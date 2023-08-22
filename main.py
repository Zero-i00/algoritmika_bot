import os

from aiogram import Bot, types, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor
from dotenv import load_dotenv
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

load_dotenv()

bot = Bot(token=os.environ.get('TOKEN'), parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class Form(StatesGroup):
    team_description = State()


@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await Form.team_description.set()
    await message.reply("Опиши команду которую ты хочешь найти.")


@dp.message_handler(state=Form.team_description)
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
        await callback.answer(text='Не хочешь как хочешь')


def main():
    executor.start_polling(dp)


if __name__ == '__main__':
    main()
