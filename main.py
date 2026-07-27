"""Оркестрация: fetch -> summarize -> deliver (Telegram + vault-заметка)."""

from dotenv import load_dotenv

load_dotenv()

from fetch import fetch_last_24h
from summarize import build_digest
from deliver_telegram import send_to_telegram
from deliver_vault_note import write_note_to_vault


def main() -> None:
    channel_posts = fetch_last_24h()
    digest = build_digest(channel_posts)

    send_to_telegram(digest)
    print("[main] дайджест отправлен в Telegram")

    write_note_to_vault(digest)
    print("[main] заметка записана в vault")


if __name__ == "__main__":
    main()
