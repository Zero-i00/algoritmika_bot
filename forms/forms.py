from aiogram.dispatcher.filters.state import StatesGroup, State


class TeamForm(StatesGroup):
    team_description = State()


class ResumeForm(StatesGroup):
    name = State()
    age = State()
    gender = State()
    hobby = State()