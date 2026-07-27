# AGENTS.md

Инструкции для AI-агентов, работающих в этом репозитории.

## Что это

Бот, который раз в день (18:00 Europe/Moscow = 15:00 UTC, cron в
`.github/workflows/daily-digest.yml`) читает Telegram-каналы из
`channels.yaml`, делает саммари через Claude и доставляет его двумя
способами: сообщением от Telegram-бота и заметкой в Obsidian-vault
(отдельный git-репозиторий, не этот).

Работает на GitHub Actions по расписанию — без своего сервера.

## Архитектура

Пайплайн линейный, каждый файл — один шаг, `main.py` их вызывает по порядку:

```
fetch.py            → Telethon (сессия личного Telegram-аккаунта) тянет
                       посты за последние 24ч по каналам из channels.yaml
summarize.py         → Anthropic API (claude-haiku-4-5) строит дайджест
deliver_telegram.py  → Telegram Bot API шлёт текст в личку пользователю
deliver_vault_note.py→ git clone/commit/push заметки в vault-репозиторий
main.py              → оркестрация: fetch → summarize → deliver x2
login_once.py         разовый локальный скрипт получения session string
                       (НЕ часть пайплайна, запускается вручную человеком)
```

Ключевое архитектурное решение: чтение (`TELEGRAM_SESSION`, доступ от
имени личного аккаунта — нужен для чтения каналов, на которые не
подписаны) и отправка (`TELEGRAM_BOT_TOKEN`, отдельный бот) разделены
намеренно, чтобы утечка одного секрета не давала полный контроль над
Telegram-аккаунтом.

## Переменные окружения / секреты

Все обязательны, читаются из `os.environ` (см. `.env.example`):

| Переменная | Назначение |
|---|---|
| `TELEGRAM_API_ID`, `TELEGRAM_API_HASH` | с my.telegram.org |
| `TELEGRAM_SESSION` | Telethon StringSession, из `login_once.py` |
| `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` | бот-доставщик через BotFather |
| `ANTHROPIC_API_KEY` | саммаризация |
| `VAULT_REPO_URL` | `https://<PAT>@github.com/<user>/<vault-repo>.git` |

В проде — GitHub Actions repository secrets (репозиторий → Settings →
Secrets and variables → Actions). Локально — `.env` (гитигнорится,
никогда не коммитить).

## Локальный запуск

```
python3 -m venv .venv && source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env   # заполнить
python main.py
```

Проверить только чтение без побочных эффектов (не шлёт и не пушит):
`python fetch.py`.

## Специфика окружения (грабли, на которые уже наступали)

- Если в системе активен conda `(base)`, `python3 -m venv` подхватывает
  conda-python вместо системного — версия может оказаться слишком старой
  для свежих пакетов (`pip` тогда молча исключает нужные версии из
  резолвера). Перед созданием venv: `conda deactivate`.
- `requirements.txt` намеренно на `>=`, а не на точных версиях — точный
  пин ловил ту же проблему с резолвером на старом `pip`.
- При редактировании `.env`/секретов вручную в GUI-редакторах — следить,
  чтобы длинные значения (особенно `VAULT_REPO_URL`) не переносились
  автопереносом строк. Перенос внутри URL ломает `git clone` в рантайме
  с ошибкой `credential url cannot be parsed`.
- `max_tokens` в `summarize.py` должен быть с запасом (сейчас 8000) —
  при большом количестве каналов ответ Claude обрезается на полуслове,
  если лимит занижен, и обрезанный текст молча уходит в Telegram.

## Секреты и данные пользователя

- `TELEGRAM_SESSION` — это не API-ключ, а живая авторизованная сессия
  личного Telegram-аккаунта (полный доступ, без пароля/2FA). Не просить
  пользователя присылать её в чат; предпочтительно, чтобы он сам вписывал
  такие значения в `.env`/GitHub secret без посредников.
- Никогда не коммитить `.env`, session-файлы, реальные токены — все уже
  в `.gitignore`, не менять это без явной причины.

## Что менять пользователю, а не агенту

- Список каналов — `channels.yaml`, редактируется руками владельца.
- Промпт саммаризации — `summarize.py::SYSTEM_PROMPT`, если нужно
  поменять тон/структуру/язык дайджеста.
