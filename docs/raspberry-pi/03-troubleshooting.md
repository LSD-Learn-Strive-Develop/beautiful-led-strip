# Ошибки и диагностика

[К оглавлению](00-summary.md)

Все Python-команды ниже выполняются на Raspberry Pi из папки проекта:

```bash
cd ~/dev/beautiful-led-strip
```

## 1. При установке rpi_ws281x не найден Python.h

Ошибка:

```text
fatal error: Python.h: No such file or directory
```

В диалоге использовался системный Python 3.13. Установите его заголовки и инструменты сборки, затем повторите установку библиотек:

```bash
sudo apt update
sudo apt install -y python3.13-dev build-essential
uv pip install adafruit-blinka adafruit-circuitpython-neopixel rpi_ws281x RPi.GPIO
```

Пересоздавать `.venv` не требуется. Для другой версии Python пакет заголовков должен соответствовать этой версии.

## 2. The platform library 'RPi' was not found

Для **Raspberry Pi 3 Model B**:

```bash
uv pip install RPi.GPIO
sudo .venv/bin/python main.py
```

Инструкцию нельзя автоматически переносить на Raspberry Pi 5: аппаратный доступ там отличается.

## 3. Погода возвращает HTTP 403

В проекте исправили две несовместимости:

1. Заголовок `X-Yandex-API-Key` заменили на `X-Yandex-Weather-Key`.
2. Для личного API перешли с REST `/v2/informers` на GraphQL `/graphql/query`.

Обновите ветку `main` и перезапустите программу. Наличие запросов в статистике кабинета не означает, что сервер разрешил доступ к данным.

Проверка текущего API напрямую, с ключом из `.env`:

```bash
.venv/bin/python - <<'PYCODE'
import os
import requests
from dotenv import load_dotenv

load_dotenv(".env", override=True)
key = os.getenv("YANDEX_WEATHER_API_KEY", "").strip()
if not key:
    raise SystemExit("YANDEX_WEATHER_API_KEY отсутствует или пуст")
lat = float(os.getenv("YANDEX_WEATHER_LAT", "59.873546"))
lon = float(os.getenv("YANDEX_WEATHER_LON", "29.827624"))
if not (-90 <= lat <= 90 and -180 <= lon <= 180):
    raise SystemExit("Проверьте координаты")
query = (
    "{ weatherByPoint(request: { lat: "
    f"{lat}, lon: {lon}"
    " }) { now { temperature } } }"
)
response = requests.post(
    "https://api.weather.yandex.ru/graphql/query",
    headers={"X-Yandex-Weather-Key": key},
    json={"query": query},
    timeout=20,
)
print("HTTP:", response.status_code)
print(response.text)
PYCODE
```

Успех — HTTP 200 и числовая температура в `data.weatherByPoint.now.temperature`. У GraphQL ошибка может находиться в поле `errors` даже при HTTP 200.

Если `403` сохраняется, проверьте ключ, активацию, доступ к API и лимиты тарифа в кабинете. Диагностика также расходует запросы. Не оставляйте многократные проверки в цикле.

## 4. ProxyTimeoutError: Proxy connection timed out

В нашем случае в `.env` сначала был указан SOCKS5 для сервера, работающего по HTTPS. Порт 443 открывался, но сервер не отвечал на SOCKS5-приветствие.

Рабочий вариант:

```dotenv
TELEGRAM_PROXY_URL=https://LOGIN:PASSWORD@de.habr.site:443
```

Нужны версия проекта с коммитом `554b97c` или новее и обновлённые зависимости:

```bash
git pull --ff-only
uv pip install -r requirements.txt
```

Затем отредактируйте `.env` и перезапустите бота. Увеличение таймаута не исправляет неправильный протокол.

### Проверить HTTPS-прокси без учётных данных

```bash
curl -I \
  --proxy https://de.habr.site:443 \
  --connect-timeout 5 \
  --max-time 15 \
  https://api.telegram.org
```

Полученный в диалоге ответ:

```text
HTTP/1.1 407 Proxy Authentication Required
Proxy-Authenticate: Basic realm="Proxy"
```

Это подтвердило, что HTTPS-прокси доступен и требует авторизацию. Сообщение curl `CONNECT tunnel failed, response 407` в этой проверке ожидаемо: пароль не передавался. Оно не подтверждает доступ к Telegram через авторизованный туннель.

### Проверить бота через прокси с данными из .env

После обновления проекта эта команда использует ту же реализацию прокси, что и бот. Она проверяет `getMe`, не запускает polling и не обращается к GPIO:

```bash
.venv/bin/python - <<'PYCODE'
import asyncio
import os
from dotenv import load_dotenv
from aiogram import Bot
from src.bot.session import TelegramSession

load_dotenv(".env", override=True)
token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
proxy = os.getenv("TELEGRAM_PROXY_URL", "").strip()
if not token or not proxy:
    raise SystemExit("Проверьте TELEGRAM_BOT_TOKEN и TELEGRAM_PROXY_URL")

async def check():
    session = TelegramSession(proxy=proxy)
    try:
        bot = Bot(token=token, session=session)
        me = await asyncio.wait_for(bot.get_me(), timeout=20)
        print(f"OK: Telegram доступен через прокси, бот @{me.username}")
    except Exception as error:
        print(type(error).__name__, str(error))
    finally:
        await session.close()

asyncio.run(check())
PYCODE
```

Если здесь снова `407`, проверьте логин, пароль и кодирование специальных символов. При ошибке сертификата проверьте время, системные сертификаты и адрес прокси; не отключайте TLS-проверку.

## 5. Как различать типы прокси

| Тип | Строка в настройках / признак |
| --- | --- |
| SOCKS5 | `socks5://LOGIN:PASSWORD@HOST:PORT` |
| HTTP CONNECT | `http://LOGIN:PASSWORD@HOST:PORT` |
| HTTPS CONNECT, TLS до прокси | `https://LOGIN:PASSWORD@HOST:PORT` |
| Telegram MTProto | Обычно ссылка `tg://proxy?...secret=...`; для этой реализации aiogram не подходит |

HTTP CONNECT может передавать HTTPS-запросы к Telegram. Схема `https://` в адресе самого прокси дополнительно включает TLS до прокси. Номер порта сам по себе протокол не определяет.

Если адрес прокси — `127.0.0.1` или `localhost`, это сама Raspberry Pi, а не компьютер, с которого вы подключились по SSH.

## 6. Бот перестал работать после выхода из SSH или перезагрузки

После выхода из SSH процесс сохраняется, если он был запущен в tmux:

```bash
tmux ls
tmux attach -t leds
```

После перезагрузки нужно запустить его снова. Постоянный автозапуск через systemd не был частью выполненной настройки.

## 7. На дисплее неправильное время

```bash
sudo timedatectl set-timezone Europe/Moscow
sudo timedatectl set-ntp true
timedatectl
date
```

Перезапустите бота после изменения часового пояса.

## Что присылать для дальнейшей диагностики

- Текст ошибки.
- Текущую ветку и коммит: `git branch --show-current` и `git log -1 --oneline`.
- Версию Python: `.venv/bin/python --version`.
- Протокол, адрес и порт прокси без логина и пароля.

Не публикуйте `.env` целиком, токен Telegram, ключ погоды или пароль прокси.
