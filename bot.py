import telebot
import threading
import time
from datetime import datetime, timedelta
from database import init_db, add_birthday, delete_birthday, get_birthdays
import sqlite3

TOKEN = '8523274938:AAFU4VR4bY8yqFtxsfYL6ngiHTbvlyErCEQ'
bot = telebot.TeleBot(TOKEN)

init_db()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, (
        "Привет! Я бот для напоминаний о днях рождения.\n"
        "Команды:\n"
        "/add — добавить день рождения\n"
        "/list — посмотреть список\n"
        "/delete — удалить запись\n"
        "Напоминания приходят за 1 день до ДР."
    ))
    
@bot.message_handler(commands=['add'])
def add_birthday_step1(message):
    msg = bot.reply_to(message, "Введите имя друга:")
    bot.register_next_step_handler(msg, process_name_step)

def process_name_step(message):
    name = message.text.strip()
    msg = bot.reply_to(message, "Введите дату рождения в формате ДД.ММ (например, 15.03):")
    bot.register_next_step_handler(msg, process_date_step, name)

def process_date_step(message, name):
    date_str = message.text.strip()
    try:
        day, month = map(int, date_str.split('.'))
        if not (1 <= day <= 31 and 1 <= month <= 12):
            raise ValueError
        db_date = f"{month:02d}-{day:02d}"
        add_birthday(message.chat.id, name, db_date)
        bot.reply_to(message, f"✅ День рождения {name} ({date_str}) сохранён!")
    except Exception:
        bot.reply_to(message, "❌ Неверный формат. Используйте ДД.ММ (например, 15.03).")

@bot.message_handler(commands=['list'])
def list_birthdays(message):
    birthdays = get_birthdays(message.chat.id)
    if not birthdays:
        bot.reply_to(message, "Список дней рождения пуст.")
    else:
        text = "📅 Ваши дни рождения:\n"
        for name, date in birthdays:
            month, day = date.split('-')
            text += f"• {name}: {day}.{month}\n"
        bot.reply_to(message, text)

@bot.message_handler(commands=['delete'])
def delete_birthday_step1(message):
    birthdays = get_birthdays(message.chat.id)
    if not birthdays:
        bot.reply_to(message, "Нечего удалять — список пуст.")
        return
    names = [name for name, _ in birthdays]
    msg = bot.reply_to(message, f"Введите имя для удаления:\nДоступные имена: {', '.join(names)}")
    bot.register_next_step_handler(msg, process_delete_step)

def process_delete_step(message):
    name = message.text.strip()
    delete_birthday(message.chat.id, name)
    bot.reply_to(message, f"🗑️ Запись о {name} удалена.")

def check_reminders():
    while True:
        today = datetime.today()
        tomorrow = today + timedelta(days=1)
        target_date = f"{tomorrow.month:02d}-{tomorrow.day:02d}"

        conn = sqlite3.connect('birthdays.db')
        cursor = conn.cursor()
        cursor.execute('SELECT user_id, name FROM birthdays WHERE date = ?', (target_date,))
        rows = cursor.fetchall()
        conn.close()

        for user_id, name in rows:
            try:
                bot.send_message(user_id, f"🔔 Завтра день рождения у {name}! Не забудьте поздравить! 🎉")
            except Exception as e:
                print(f"Не удалось отправить сообщение пользователю {user_id}: {e}")

        time.sleep(24 * 60 * 60)

reminder_thread = threading.Thread(target=check_reminders, daemon=True)
reminder_thread.start()

if __name__ == '__main__':
    print("Бот запущен...")
    bot.polling(none_stop=True)