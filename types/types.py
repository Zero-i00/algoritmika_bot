from dataclasses import dataclass


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

