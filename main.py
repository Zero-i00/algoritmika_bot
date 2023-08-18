import os

from aiogram.utils import executor
from aiogram import Bot, types, Dispatcher
from dotenv import load_dotenv
load_dotenv()

bot = Bot(token=os.environ.get('TOKEN'), parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)


@dp.message_handler(commands='start')
async def start(message: types.Message):
    await message.answer('''
Здравствуйте, этот бот создан
для того чтобы помочь найти вам команду.
Надеемся что у вас это получится
и опасайтесь мошенников.''')
def main():
    executor.start_polling(dp)

if __name__ == '__main__':
    main()







