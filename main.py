import os

from aiogram.utils import executor
from aiogram import Bot, types, Dispatcher


bot = Bot(token=os.environ.get('TOKEN'), parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)


@dp.message_handler(commands='start')
async def start(message: types.Message):
    await message.answer('Hello some')


def main():
    executor.start_polling(dp)


if __name__ == '__main__':
    main()
