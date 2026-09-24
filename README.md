# 🎄 Beautiful LED Strip

LED strip controller for displaying time, temperature, countdown to New Year, and custom text.
Controlled via Telegram bot.

## Features

- ⏰ **Time Display** — Shows current time in HHMM format
- 🌡 **Temperature** — Fetches and displays current temperature (Yandex Weather API)
- 🎉 **Countdown** — New Year countdown with fast mode in final minute
- 📝 **Custom Text** — Scrolling text display (admin only)
- 🌈 **Rainbow Effect** — Full spectrum color animation
- 💜 **Color Control** — Change display color via emoji reactions

## Hardware

- Raspberry Pi
- 392-pixel NeoPixel LED strip (4 digits × 7 segments × 14 LEDs)
- Connected to GPIO pin D18

## Documentation

**`main` is the primary branch for installation and updates.** The working
Raspberry Pi 3 Model B setup, including the authenticated HTTPS proxy, was
confirmed on 24 September 2026.

- [Setup summary and working configuration (RU)](docs/raspberry-pi/00-summary.md)
- [Raspberry Pi: Wi-Fi, SSH, time and tools (RU)](docs/raspberry-pi/01-raspberry-pi-setup.md)
- [Installation, operation and migration from refactoring to main (RU)](docs/raspberry-pi/02-project-operation.md)
- [Troubleshooting Python, weather and proxy errors (RU)](docs/raspberry-pi/03-troubleshooting.md)

## Installation

The following commands target Raspberry Pi 3 Model B with Debian and uv.

1. Clone the primary branch:
   ```bash
   git clone --branch main https://github.com/LSD-Learn-Strive-Develop/beautiful-led-strip.git
   cd beautiful-led-strip
   ```

2. Install build dependencies and create a Python environment:
   ```bash
   sudo apt update
   sudo apt install -y python3-dev build-essential
   uv venv --python /usr/bin/python3
   uv pip install -r requirements.txt
   ```
   Use Python 3.11 or newer for HTTPS proxy support. If you select a non-default
   Python version, install matching development headers.

3. Install Raspberry Pi 3 hardware libraries:
   ```bash
   uv pip install adafruit-blinka adafruit-circuitpython-neopixel rpi_ws281x RPi.GPIO
   ```

4. Create `.env` if it does not already exist, then fill in your credentials:
   ```bash
   cp -n .env.example .env
   nano .env
   ```
   ```env
   TELEGRAM_BOT_TOKEN=your_bot_token
   TELEGRAM_ADMIN_ID=123456789
   YANDEX_WEATHER_API_KEY=your_weather_api_key
   ```

### Optional Telegram proxy

Install the dependencies into your existing uv environment:

```bash
uv pip install -r requirements.txt
```

Set the proxy URL in `.env`:

```env
TELEGRAM_PROXY_URL=socks5://user:password@proxy.example.com:1080
```

Use `socks5://host:port` without authentication, or `http://host:port` for an
HTTP CONNECT proxy. For a TLS-encrypted connection to the proxy, use
`https://user:password@host:443` (Python 3.11 or newer). Certificates are
verified for both the proxy and Telegram. A `407` response means the proxy
requires valid credentials. Percent-encode special characters in the username and
password (for example, `@` becomes `%40`). MTProto proxies are not supported.
Leave the variable empty or omit it to connect directly.

The proxy applies only to Telegram Bot API requests, including polling;
weather requests keep their existing connection settings. Restart the bot
after changing `.env`. On Raspberry Pi with a uv environment:

```bash
sudo .venv/bin/python main.py
```

### Yandex Weather API

Weather uses API v3 (GraphQL), as in Yandex's official personal smart-home
integration: `POST https://api.weather.yandex.ru/graphql/query` with the
`X-Yandex-Weather-Key` header. Keep the key in `YANDEX_WEATHER_API_KEY` in `.env`.
The request fetches only the current temperature for `YANDEX_WEATHER_LAT` and
`YANDEX_WEATHER_LON`. Legacy REST-only keys may require a different API plan.

Reference: https://yandex.ru/dev/weather/doc/ru/concepts/how-to

## Usage

Run from the project directory on the Raspberry Pi:

```bash
sudo .venv/bin/python main.py
```

### Telegram Commands

- `/start` — Start the bot and show control keyboard
- `/help` — Show help message

### Control via Emoji

Send any heart emoji (❤️ 🧡 💛 💚 💙 💜 🖤 🤍 🤎) to change the display color.

Special actions:
- 🌈 — Show rainbow animation
- 🌡 — Show current temperature

### Modes

Send mode name as text message to switch between display modes:

#### MAIN (основной режим)
- **Активация**: отправьте `main`
- **Поведение**:
  - При смене минуты автоматически показывает температуру (5 сек), затем время (5 сек)
  - Если цвет чёрный, автоматически заменяется случайным существующим цветом
  - При изменении цвета или радуги перерисовывает время
- **Интервал обновления**: 5 секунд

#### USER (пользовательский режим)
- **Активация**: отправьте `user`
- **Поведение**:
  - При смене минуты показывает температуру (5 сек), затем прокручиваемый текст "С НОВЫМ ГОДОМ", затем время (5 сек)
  - Если цвет чёрный, автоматически заменяется случайным существующим цветом
  - При изменении цвета или радуги перерисовывает время
- **Интервал обновления**: 5 секунд
- **Автоматический переход**: режим FIGHT автоматически переключается в USER после завершения обратного отсчёта

#### FIGHT (режим обратного отсчёта)
- **Активация**: отправьте `fight`
- **Поведение**:
  - Показывает обратный отсчёт до Нового года
  - Обновляется при изменении значения, цвета, радуги или при запросе обновления
  - Автоматически переключается в режим **FIGHT_FAST** в последнюю минуту
- **Интервал обновления**: 5 секунд

#### FIGHT_FAST (быстрый режим обратного отсчёта)
- **Активация**: автоматически активируется в последнюю минуту обратного отсчёта
- **Поведение**:
  - Показывает обратный отсчёт с быстрыми обновлениями
  - При завершении отсчёта:
    - Переключается в режим **USER**
    - Показывает прокручиваемый текст "С НОВЫМ ГОДОМ! 🎉"
    - Запускает радужный цикл
- **Интервал обновления**: 0.5 секунды (быстрее, чем в других режимах)

#### Общие особенности всех режимов
- Обработка ожидающего текста (прокручивается при наличии)
- Запрос температуры (показывается статично)
- Радужная анимация (5 секунд при включении)

## Project Structure

```
beautiful-led-strip/
├── main.py                 # Entry point
├── src/
│   ├── config.py           # Configuration from .env
│   ├── led/
│   │   ├── controller.py   # LED hardware control
│   │   ├── symbols.py      # Character definitions
│   │   └── effects.py      # Visual effects
│   ├── display/
│   │   ├── time_display.py # Time rendering
│   │   ├── countdown.py    # Countdown logic
│   │   └── text_display.py # Text rendering
│   ├── services/
│   │   └── weather.py      # Weather API integration
│   └── bot/
│       ├── main.py         # Bot initialization
│       ├── keyboards.py    # Telegram keyboards
│       └── handlers/       # Message handlers
├── data/                   # Runtime data (color, weather cache)
├── .env.example            # Environment template
└── requirements.txt        # Python dependencies
```

## License

MIT