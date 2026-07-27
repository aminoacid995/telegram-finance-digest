"""Отправляет готовый текст дайджеста через Telegram Bot API."""

import os
import urllib.request
import urllib.parse
import json

TELEGRAM_MESSAGE_LIMIT = 4096


def _chunk(text: str, limit: int = TELEGRAM_MESSAGE_LIMIT) -> list[str]:
    chunks = []
    while text:
        chunks.append(text[:limit])
        text = text[limit:]
    return chunks


def send_to_telegram(text: str) -> None:
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]
    url = f"https://api.telegram.org/bot{token}/sendMessage"

    for chunk in _chunk(text):
        payload = urllib.parse.urlencode({"chat_id": chat_id, "text": chunk}).encode()
        req = urllib.request.Request(url, data=payload, method="POST")
        with urllib.request.urlopen(req) as resp:
            body = json.loads(resp.read())
            if not body.get("ok"):
                raise RuntimeError(f"Telegram API error: {body}")
