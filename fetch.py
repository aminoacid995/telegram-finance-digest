"""Тянет посты за последние 24 часа из каналов, перечисленных в channels.yaml."""

import os
import datetime
from dataclasses import dataclass

import yaml
from telethon.sync import TelegramClient
from telethon.sessions import StringSession


@dataclass
class ChannelPosts:
    channel: str
    title: str
    posts: list[str]


def load_channels(path: str = "channels.yaml") -> list[str]:
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data.get("channels") or []


def fetch_last_24h(hours: int = 24) -> list[ChannelPosts]:
    api_id = int(os.environ["TELEGRAM_API_ID"])
    api_hash = os.environ["TELEGRAM_API_HASH"]
    session = os.environ["TELEGRAM_SESSION"]

    since = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=hours)
    channels = load_channels()
    result: list[ChannelPosts] = []

    with TelegramClient(StringSession(session), api_id, api_hash) as client:
        for username in channels:
            try:
                entity = client.get_entity(username)
            except Exception as exc:
                print(f"[fetch] пропускаю {username}: {exc}")
                continue

            posts = []
            for message in client.iter_messages(entity, offset_date=None, reverse=False):
                if message.date < since:
                    break
                if message.message:
                    posts.append(message.message)

            title = getattr(entity, "title", username)
            result.append(ChannelPosts(channel=username, title=title, posts=posts))
            print(f"[fetch] {username}: {len(posts)} постов за последние {hours}ч")

    return result


if __name__ == "__main__":
    for cp in fetch_last_24h():
        print(f"\n=== {cp.title} (@{cp.channel}) — {len(cp.posts)} постов ===")
        for p in cp.posts[:3]:
            print("-", p[:120].replace("\n", " "))
