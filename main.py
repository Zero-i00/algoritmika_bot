import os

from aiogram.dispatcher.filters import Text
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils import executor
from aiogram import Bot, types, Dispatcher
from dotenv import load_dotenv

from Types.message_type import RedirectMessageType

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


def handle_redirect(text: str) -> RedirectMessageType | None:
    processed: str = text.lower()

    match processed:
        case 'Помощь':
            return RedirectMessageType(
                title="помощь",
                description="Нажмите накнопку чтоб перейти к боту"
            )
        case "найти команду":
            return RedirectMessageType(
                title="Поиск команды",
                description="Нажмите накнопку чтобы перейти к боту"
            )
        case "Моё":
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

    print(message.chat.id)

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


def main():
    executor.start_polling(dp)


if __name__ == '__main__':
    main()
