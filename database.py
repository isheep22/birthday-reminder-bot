import sqlite3
from datetime import datetime

DB_NAME = 'birthdays.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS birthdays (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            date TEXT NOT NULL  
        )
    ''')
    conn.commit()
    conn.close()

def add_birthday(user_id: int, name: str, date: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO birthdays (user_id, name, date) VALUES (?, ?, ?)', (user_id, name, date))
    conn.commit()
    conn.close()

def delete_birthday(user_id: int, name: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM birthdays WHERE user_id = ? AND name = ?', (user_id, name))
    conn.commit()
    conn.close()

def get_birthdays(user_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT name, date FROM birthdays WHERE user_id = ?', (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows  