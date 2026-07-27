"""Строит текстовый дайджест из постов через Anthropic API."""

import os

import anthropic

from fetch import ChannelPosts

MODEL = "claude-haiku-4-5"

SYSTEM_PROMPT = """\
Ты помогаешь собрать ежедневный дайджест финансовых новостей из Telegram-\
каналов. На вход — посты за последние 24 часа, сгруппированные по каналам.

Сделай:
1. Блок "Главное" сверху: 3-5 буллетов с самым важным за день по всем \
каналам вместе.
2. Дальше по каждому каналу, где были посты: 2-4 буллета с сутью (не \
пересказывай каждый пост, выбирай важное).
3. Если по каналу за 24 часа не было постов, не упоминай его.
4. Пиши на том же языке, на котором был исходный пост (не переводи \
принудительно, оставляй как в оригинале).
5. Никакой воды, вступлений и заключений — только структура выше.
"""


def build_digest(channel_posts: list[ChannelPosts]) -> str:
    non_empty = [cp for cp in channel_posts if cp.posts]
    if not non_empty:
        return "За последние 24 часа новых постов в отслеживаемых каналах не было."

    source_text = "\n\n".join(
        f"### Канал: {cp.title} (@{cp.channel})\n" + "\n---\n".join(cp.posts)
        for cp in non_empty
    )

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    response = client.messages.create(
        model=MODEL,
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": source_text}],
    )
    return response.content[0].text
