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

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/beautiful-led-strip.git
   cd beautiful-led-strip
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Install Raspberry Pi specific libraries:
   ```bash
   pip install board neopixel
   ```

4. Create `.env` file from example:
   ```bash
   cp .env.example .env
   ```

5. Edit `.env` with your credentials:
   ```env
   TELEGRAM_BOT_TOKEN=your_bot_token
   TELEGRAM_ADMIN_ID=your_telegram_id
   YANDEX_WEATHER_API_KEY=your_weather_api_key
   ```

## Usage

```bash
python main.py
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