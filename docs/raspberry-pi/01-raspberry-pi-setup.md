# Подготовка Raspberry Pi через консоль

[К оглавлению](00-summary.md)

Команды выполняются **на Raspberry Pi**. В диалоге использовалась Raspberry Pi 3 Model B с Debian и Python 3.13.

## 1. Подключение к Wi-Fi

Эти команды подходят для системы с NetworkManager, в том числе Raspberry Pi OS Bookworm и новее.

```bash
sudo nmcli radio wifi on
nmcli device wifi list
sudo nmcli --ask device wifi connect "Имя сети"
```

Замените имя сети своим. Пароль будет запрошен отдельно. Соединение сохраняется для следующих запусков.

Проверка:

```bash
nmcli device status
hostname -I
ping -c 3 raspberrypi.com
```

Если Wi-Fi заблокирован:

```bash
sudo rfkill unblock wifi
```

На Raspberry Pi OS страну Wi-Fi можно задать через:

```bash
sudo raspi-config
```

Выберите `Localisation Options → WLAN Country` и фактическую страну нахождения. В обычном Debian утилита `raspi-config` может отсутствовать.

Если нет `nmcli`, сначала уточните ОС и используемый сетевой менеджер:

```bash
cat /etc/os-release
```

## 2. Включение SSH

```bash
sudo systemctl enable --now ssh
sudo systemctl status ssh
hostname -I
whoami
```

Если служба `ssh` не найдена, установите сервер и включите её:

```bash
sudo apt update
sudo apt install openssh-server
sudo systemctl enable --now ssh
```

С другого компьютера в той же сети:

```bash
ssh pi@192.168.1.100
```

Замените `pi` и IP-адрес на значения своей Raspberry Pi.

## 3. Московское время

Часовой пояс и синхронизация часов — разные настройки. Задайте обе:

```bash
sudo timedatectl set-timezone Europe/Moscow
sudo timedatectl set-ntp true
timedatectl
date
```

Ожидается `Time zone: Europe/Moscow` и после синхронизации `System clock synchronized: yes`. Нужен доступ в интернет.

Если Debian сообщает, что NTP не поддерживается, нужно проверить установленную службу синхронизации времени. Не меняйте время вручную вместо диагностики службы.

После изменения часового пояса перезапустите бота.

## 4. Git, tmux и инструменты установки

```bash
sudo apt update
sudo apt install -y git tmux curl ca-certificates
```

Проверка Git:

```bash
git --version
```

Для создания собственных коммитов можно настроить автора:

```bash
git config --global user.name "Ваше имя"
git config --global user.email "you@example.com"
```

Для скачивания и обновления проекта настройка автора не требуется.

## 5. Установка uv

Официальный установщик запускается от обычного пользователя, без `sudo`:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source "$HOME/.local/bin/env"
uv --version
```

Установщик обычно настраивает PATH. Если после нового входа команда `uv` не находится, добавьте путь в Bash:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
uv --version
```

Добавлять эту строку достаточно один раз.

## 6. tmux: основные команды

Создать сессию:

```bash
tmux new -s leds
```

Отсоединиться с сохранением работающего процесса: **Ctrl+B**, отпустить клавиши, затем **D**.

Список сессий и возврат:

```bash
tmux ls
tmux attach -t leds
```

Остановить программу внутри сессии: **Ctrl+C**.

## Источники

- [Настройка Raspberry Pi](https://www.raspberrypi.com/documentation/computers/configuration.html).
- [Установка uv](https://docs.astral.sh/uv/getting-started/installation/).
