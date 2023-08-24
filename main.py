import os
import aiogram.utils.markdown as md
from aiogram.dispatcher import FSMContext
from aiogram.utils import executor
from aiogram import Bot, types, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import firebase_admin
from dacite import from_dict
from firebase_admin import credentials, db
from firebase_admin import storage, firestore

from aiogram.dispatcher.filters import Text
from dataclasses import dataclass
from dotenv import load_dotenv
from google.api_core.datetime_helpers import DatetimeWithNanoseconds

load_dotenv()


@dataclass
class RedirectMessageType:
    title: str
    description: str


@dataclass
class Resume:
    chat_id: str
    FIO: str
    age: int
    about: str
    skills: str


class TeamForm(StatesGroup):
    team_description = State()


class ResumeForm(StatesGroup):
    name = State()
    age = State()
    gender = State()
    hobby = State()


bot = Bot(token=os.environ.get('TOKEN'), parse_mode=types.ParseMode.HTML)
st = MemoryStorage()
dp = Dispatcher(bot, storage=st)

cred = credentials.Certificate("maga-cd4dd-firebase-adminsdk-3gdqy-23f2874c71.json")
database_url = {
    'databaseUrl': 'https://maga-cd4dd-firebaseio.com'
}
firebase_admin.initialize_app(cred, database_url)


database = firestore.client()
col_ref = database.collection('user_info')


def create_resume(resume: Resume) -> DatetimeWithNanoseconds | None:
    return col_ref.add({
        'chat_id': resume.chat_id,
        'FIO': resume.FIO,
        'age': resume.age,
        'about': resume.about,
        'skills': resume.skills,
    })


async def get_resume_by_chat_id(chat_id: str) -> dict | None:
    for response in col_ref.get():
        value = response.to_dict()
        if value.get('chat_id') == chat_id:
            return value

    return None


def update_resume_by_chat_id(chat_id: str, resume: Resume) -> None:
    user = col_ref.where('chat_id', '==', chat_id).get()
    if not user:
        return
    buf_user = col_ref.document(user[0].id)
    buf_user.set({
        'chat_id': chat_id,
        'FIO': resume.FIO,
        'age': resume.age,
        'about': resume.about,
        'skills': resume.skills,
    })


@dp.message_handler(commands=['start'])
async def start(message: types.Message) -> None:
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
    await message.answer('Опиши команду, которую ты хочешь найти.')


@dp.message_handler(Text(equals='Моё резюме'))
async def get_resume(message: types.Message):
    await message.answer('Подождите, мы ищем ваше резюме....')
    resume = await get_resume_by_chat_id(chat_id=message.chat.id)
    keyboard = InlineKeyboardMarkup()
    if resume:
        ink = InlineKeyboardButton('Редактировать', callback_data='bu')
        keyboard.add(ink)
        await message.answer(
            text=
            f'''
{md.text('ФИО:', md.bold(resume.get('FIO')))}
{md.text('Возраст:', md.code(resume.get('age'), get_age_postfix(resume.get('age'))))}
{md.text('Достоинства:', resume.get('skills'))}
{md.text('О себе:', md.bold(resume.get('about')))}
''',
            reply_markup=keyboard
        )
    else:
        ink = InlineKeyboardButton('Создать резюме', callback_data='bu')
        keyboard.add(ink)
        await message.answer(
            text='''
        У вас пока что нет резюме, cоздайте его.''',
            reply_markup=keyboard
        )


@dp.callback_query_handler(lambda c: c.data == 'bu')
async def process_callback_button1(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await ResumeForm.name.set()
    await bot.send_message(callback_query.from_user.id,"Укажите ваше ФИО")

def handle_redirect(text: str) -> RedirectMessageType | None:
    processed: str = text.lower()

    match processed:
        case 'help':
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


@dp.message_handler(state=ResumeForm.name)
async def process_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
    await ResumeForm.next()
    await message.reply("Сколько вам лет?")


@dp.message_handler(lambda message: not message.text.isdigit(), state=ResumeForm.age)
async def process_age_invalid(message: types.Message):
    return await message.reply("Это не число!")


# Принимаем возраст и узнаём пол
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
    await message.reply("Расскажите немного о себе")


def get_age_postfix(age):
    k = int(age) % 10
    if k == 1 and (10 > k or k > 20):
        t = "год"
    elif 1 < k < 5 and (10 > k or k > 20):
        t = "года"
    else:
        t = "лет"
    return t


@dp.message_handler(state=ResumeForm.hobby)
async def process_gender(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['hobby'] = message.text
        keyboard = InlineKeyboardMarkup()
        inline_btn_1 = InlineKeyboardButton('Сохранить', callback_data='button_resume_send')
        keyboard.add(inline_btn_1)
        inline_btn_2 = InlineKeyboardButton('Редактировать', callback_data='bu1')
        keyboard.add(inline_btn_2)
        await message.answer(
            md.text(
                md.text('ФИО:', md.bold(data['name'])),
                md.text('Возраст:', md.code(data['age'], get_age_postfix(data['age']))),
                md.text('Достоинства:', data['gender']),
                md.text('О себе:', md.bold(data['hobby'])),
                sep='\n',
            ),
            reply_markup=keyboard
        )


@dp.callback_query_handler(lambda c: c.data == 'bu1', state=ResumeForm)
async def process_callback_button1(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await state.finish()
    await ResumeForm.name.set()
    await bot.send_message(callback_query.from_user.id,"Укажите ваше ФИО")


@dp.callback_query_handler(lambda c: c.data == 'button_resume_send', state=ResumeForm)
async def process_callback_button1(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    async with state.proxy() as data:
        resume = Resume(
            chat_id=callback_query.from_user.id,
            FIO=data['name'],
            age=int(data['age']),
            about=data['gender'],
            skills=data['hobby'],
        )

        is_has_resume = await get_resume_by_chat_id(chat_id=callback_query.from_user.id)

        if is_has_resume:
            update_resume_by_chat_id(
                chat_id=callback_query.from_user.id,
                resume=resume
            )
            await bot.send_message(callback_query.from_user.id, 'Резюме успешно обнавлено')
        else:
            is_created = create_resume(resume)
            if is_created:
                await bot.send_message(callback_query.from_user.id, 'Резюме успешно создано')
            else:
                await bot.send_message(callback_query.from_user.id, 'Что-то пошло не так')
    await state.finish()


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
        await callback.answer(text='Не хочешь как хочешь')


def main():
    executor.start_polling(dp)


if __name__ == '__main__':
    main()
