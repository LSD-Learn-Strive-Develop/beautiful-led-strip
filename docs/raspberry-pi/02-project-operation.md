# Beautiful LED Strip: установка и эксплуатация

[К оглавлению](00-summary.md)

Инструкция для Raspberry Pi 3 Model B. Итоговая рабочая ветка — **`main`**. Команды выполняются на Raspberry Pi, а не на компьютере, с которого открыт SSH.

## 1. Скачать проект или обновить существующий

Для первой установки:

```bash
mkdir -p ~/dev
cd ~/dev
git clone --branch main https://github.com/LSD-Learn-Strive-Develop/beautiful-led-strip.git
cd beautiful-led-strip
```

Если проект уже скачан:

```bash
cd ~/dev/beautiful-led-strip
git status --short --branch
git switch main
git pull --ff-only
```

Если Git сообщает о конфликте локальных изменений, сначала разберите эти изменения; не удаляйте их принудительным сбросом.

### Перейти с прежней ветки refactoring

Остановите запущенного бота через **Ctrl+C**, затем выполните:

```bash
cd ~/dev/beautiful-led-strip
git status --short --branch
git fetch origin
git switch main
git pull --ff-only origin main
uv pip install -r requirements.txt
sudo .venv/bin/python main.py
```

Существующие `.env` и `.venv` сохраняются. Если локальной ветки `main` ещё нет,
`git switch main` обычно создаст её из `origin/main`. Если Git не смог выбрать
удалённую ветку автоматически, выполните `git switch --track origin/main`.
При сообщении о локальных изменениях сначала разберите их, не применяя
принудительный сброс.

## 2. Подготовить Python и установить зависимости

В нашей системе использовался `/usr/bin/python3` версии 3.13. Проверьте версию:

```bash
/usr/bin/python3 --version
```

Для Debian с Python 3.13:

```bash
sudo apt update
sudo apt install -y python3.13-dev build-essential
```

Если системный Python другой версии, нужен соответствующий пакет разработки; `python3-dev` устанавливает заголовки стандартного Python текущего Debian.

Окружение создайте один раз:

```bash
uv venv --python /usr/bin/python3
```

Установка зависимостей:

```bash
uv pip install -r requirements.txt
uv pip install adafruit-blinka adafruit-circuitpython-neopixel rpi_ws281x RPi.GPIO
```

`board` и `neopixel` — имена импортируемых модулей. Правильные пакеты для этой установки: `adafruit-blinka` и `adafruit-circuitpython-neopixel`. Не повторяйте старую команду `pip install board neopixel` из исходной инструкции.

Зависимости устанавливаются без `sudo`, в `.venv`. При обновлении проекта пересоздавать окружение не нужно.

## 3. Настроить .env

При первой настройке скопируйте пример, сохраняя существующий файл, если он уже есть:

```bash
cp -n .env.example .env
nano .env
```

Пример конфигурации; замените заглушки своими значениями:

```dotenv
TELEGRAM_BOT_TOKEN=YOUR_BOT_TOKEN
TELEGRAM_ADMIN_ID=123456789
TELEGRAM_PROXY_URL=https://LOGIN:PASSWORD@de.habr.site:443

YANDEX_WEATHER_API_KEY=YOUR_WEATHER_API_KEY
YANDEX_WEATHER_LAT=59.873546
YANDEX_WEATHER_LON=29.827624
WEATHER_CACHE_MINUTES=30

LED_PIN=D18
LED_COUNT=392
```

`TELEGRAM_ADMIN_ID` — числовой ID администратора. Координаты и число светодиодов приведены из конфигурации проекта; измените их для своей установки.

Для режима обратного отсчёта отдельно проверьте `NEW_YEAR_DATE`: в старом примере было `2026-01-01 00:00:00`. Задайте нужную будущую дату в формате `YYYY-MM-DD HH:MM:SS`.

### HTTPS-прокси

Рабочий протокол этого сервера — **HTTPS**, поэтому используйте именно `https://`.

```dotenv
TELEGRAM_PROXY_URL=https://LOGIN:PASSWORD@de.habr.site:443
```

В логине и пароле специальные символы должны быть закодированы для URL, например:

| Символ | Код |
| --- | --- |
| `@` | `%40` |
| `#` | `%23` |
| `:` | `%3A` |
| `/` | `%2F` |
| `%` | `%25` |

Кодируйте только логин и пароль, а не всю строку адреса. Например, пароль `p@ss` записывается как `p%40ss`.

Поддержка HTTPS-прокси добавлена в коммите `554b97c`. Нужны обновлённые зависимости; для этого варианта используйте Python 3.11 или новее. Наша конфигурация — Python 3.13.

Пустая или отсутствующая переменная `TELEGRAM_PROXY_URL` означает прямое подключение. Настройка применяется к Telegram; погодный сервис использует своё HTTP-подключение.

После редактирования `.env` перезапустите процесс.

### Яндекс Погода для личного использования

Текущий код использует API v3:

- Метод: `POST`.
- Адрес: `https://api.weather.yandex.ru/graphql/query`.
- Заголовок: `X-Yandex-Weather-Key`.
- Запрашиваемое поле: `weatherByPoint → now → temperature`.
- Ключ берётся из `YANDEX_WEATHER_API_KEY`.

В старом коде использовались `/v2/informers` и `X-Yandex-API-Key`; для нашей настройки этого было недостаточно. После перехода на v3 имя переменной в `.env` не меняется.

Интервал кэша по умолчанию — 30 минут. При постоянной работе это примерно 48 успешных обновлений в сутки. Сверьте интервал с лимитами именно своего тарифа; перезапуски, диагностика и ошибки могут увеличивать число запросов.

## 4. Проверить аппаратную настройку

Проект использует `board.D18`: это GPIO18 (BCM), а не физический контакт 18.

Для NeoPixel на GPIO18 инструкция Adafruit требует отключить встроенный PWM-звук: параметр `dtparam=audio=off` в действующем файле загрузочной конфигурации, затем перезагрузка. В Raspberry Pi OS файл часто находится в `/boot/firmware/config.txt`, в старых установках — `/boot/config.txt`. Путь зависит от образа ОС; не создавайте файл вслепую.

В диалоге отдельная проверка этой настройки не выполнялась. Если установка уже работает, повторно менять её не нужно.

## 5. Запустить

```bash
cd ~/dev/beautiful-led-strip
sudo .venv/bin/python main.py
```

Используется Python именно из окружения `uv`. Права администратора нужны аппаратному драйверу NeoPixel на этой конфигурации. Активировать окружение вручную не требуется.

## 6. Оставить работать после выхода из SSH

При первом запуске в tmux:

```bash
cd ~/dev/beautiful-led-strip
tmux new -s leds
sudo .venv/bin/python main.py
```

Нажмите **Ctrl+B**, затем **D**. Теперь можно выйти из SSH.

Вернуться:

```bash
tmux attach -t leds
```

Если сессия `leds` уже существует, подключитесь к ней; не запускайте ещё одну копию бота. После перезагрузки Raspberry Pi tmux не восстанавливает процесс автоматически.

## 7. Обновить работающую установку

Вернитесь в сессию и остановите бота через **Ctrl+C**:

```bash
tmux attach -t leds
```

Затем:

```bash
cd ~/dev/beautiful-led-strip
git branch --show-current
git pull --ff-only
uv pip install -r requirements.txt
sudo .venv/bin/python main.py
```

Ожидаемая ветка — `main`. `.env` хранится локально и не включён в Git. Не заменяйте его примером при каждом обновлении.

## Источники

- [Репозиторий и рабочая ветка](https://github.com/LSD-Learn-Strive-Develop/beautiful-led-strip/tree/main).
- [NeoPixel на Raspberry Pi](https://learn.adafruit.com/neopixels-on-raspberry-pi/python-usage).
- [Яндекс Погода API v3](https://yandex.com/dev/weather/doc/ru/concepts/how-to).
- [Официальная интеграция Яндекса для умного дома](https://github.com/yandex/pogoda-home-assistant).
