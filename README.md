# Telegram Finance Digest

Раз в день (18:00 по Москве) читает список Telegram-каналов о финансах,
делает summary через Claude и присылает его двумя способами:
1. сообщением от Telegram-бота вам в личку;
2. заметкой в Obsidian-vault (`Resources/finance/`).

Работает на GitHub Actions по расписанию — не требует своего сервера.

## Разовая настройка

### 1. Telegram API credentials
Зайдите на https://my.telegram.org → API development tools → создайте
приложение, возьмите `api_id` и `api_hash`.

### 2. Session string (доступ к аккаунту на чтение)
```
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python login_once.py
```
Введите `api_id`, `api_hash`, номер телефона и код из Telegram. Скрипт
выведет session string — это секрет `TELEGRAM_SESSION`, храните как пароль.

### 3. Бот для доставки сообщений
В Telegram напишите @BotFather → `/newbot` → получите `TELEGRAM_BOT_TOKEN`.
Затем напишите что угодно этому боту и откройте в браузере:
```
https://api.telegram.org/bot<TOKEN>/getUpdates
```
Найдите `"chat":{"id": ...}` — это `TELEGRAM_CHAT_ID`.

### 4. Anthropic API key
https://console.anthropic.com → API Keys → создать ключ (`ANTHROPIC_API_KEY`).

### 5. Список каналов
Заполните `channels.yaml` юзернеймами (без `@`).

### 6. Доступ к репозиторию vault
Создайте Personal Access Token на GitHub (Settings → Developer settings →
Personal access tokens) с правом `repo` только на репозиторий vault.
`VAULT_REPO_URL` = `https://<token>@github.com/<user>/<vault-repo>.git`.

### 7. Секреты в GitHub Actions
В репозитории бота: Settings → Secrets and variables → Actions → New
repository secret. Добавить все семь:
`TELEGRAM_API_ID`, `TELEGRAM_API_HASH`, `TELEGRAM_SESSION`,
`TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, `ANTHROPIC_API_KEY`,
`VAULT_REPO_URL`.

## Локальный тест

```
cp .env.example .env   # заполнить значениями
pip install -r requirements.txt
python main.py
```

Проверьте, что пришло сообщение в Telegram и появился файл в клоне vault
(смотрите вывод `[vault] ...` в консоли — путь временной директории).

## Запуск в облаке

После того как секреты добавлены, запустите workflow вручную: repo →
Actions → Daily finance digest → Run workflow. Дальше он будет запускаться
каждый день в 15:00 UTC (18:00 МСК) автоматически.

## Известные ограничения

- Если каналов много и постов за день накопится очень много, весь текст
  разом уходит в один вызов Claude без чанкинга — при разрастании списка
  каналов стоит добавить разбивку на батчи.
- `login_once.py` создаёт долгоживущую сессию личного аккаунта. Если она
  когда-либо "утечёт" — немедленно завершите сессии устройства в Telegram
  (Settings → Devices) и перегенерируйте.
