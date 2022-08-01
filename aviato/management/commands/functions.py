import sqlite3
from config import admin

connection = sqlite3.connect('data.db')
q = connection.cursor()


async def antiflood(*args, **kwargs):
    m = args[0]
    if m.chat.id == admin:
        pass
    else: 
        await m.answer("Сработал антифлуд! Прекрати флудить и жди 3 секунды.")