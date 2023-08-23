import firebase_admin
from firebase_admin import credentials, firestore
from google.api_core.datetime_helpers import DatetimeWithNanoseconds

from types.types import Resume

cred = credentials.Certificate("./maga-cd4dd-firebase-adminsdk-3gdqy-23f2874c71.json")
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

async def update_resume_by_chat_id(chat_id: str, resume: Resume) -> None:
    user = await col_ref.where('chat_id', '==', chat_id).get()
    if not user:
        return
    buf_user = await col_ref.document(user[0].id)
    await buf_user.set({
        'chat_id': chat_id,
        'FIO': resume.FIO,
        'age': resume.age,
        'about': resume.about,
        'skills': resume.skills,
    })


async def get_resume_by_chat_id(chat_id: str) -> Resume | None:
    user = await col_ref.where('chat_id', '==', chat_id).get()
    if not user:
        return

    return user[0].to_dict()