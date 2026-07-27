"""
Разовый локальный логин в Telegram через Telethon.

Запускается ОДИН РАЗ вручную на вашем компьютере (не в GitHub Actions).
Спросит номер телефона, код из Telegram и, если включена, 2FA-пароль.
В конце распечатает session string — его нужно положить в GitHub Actions
secret TELEGRAM_SESSION и больше никогда никому не показывать: это полный
доступ к вашему Telegram-аккаунту.

Использование:
    pip install -r requirements.txt
    python login_once.py
"""

from telethon.sync import TelegramClient
from telethon.sessions import StringSession

API_ID = input("TELEGRAM_API_ID (с my.telegram.org): ").strip()
API_HASH = input("TELEGRAM_API_HASH (с my.telegram.org): ").strip()

with TelegramClient(StringSession(), int(API_ID), API_HASH) as client:
    session_string = client.session.save()
    print("\nГотово. Session string (сохраните как secret TELEGRAM_SESSION):\n")
    print(session_string)
    print("\nНикому не передавайте эту строку и не коммитьте её в git.")
