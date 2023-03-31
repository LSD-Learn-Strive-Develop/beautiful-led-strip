import board
import neopixel
import time
import asyncio
from datetime import datetime
from multiprocessing import Process, Value
import subprocess
import sys

#subprocess.check_call([sys.executable, "-m", "pip", "install", "-U", "--pre", "aiogram"])
print("ok")
from aiogram import Bot, types, Dispatcher
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.filters.command import Command
from aiogram import F

from config import TOKEN

import json
import requests
from requests.structures import CaseInsensitiveDict

url = "https://api.weather.yandex.ru/v2/informers?lat=59.873546&lon=29.827624&lang=ru_RU"

headers = CaseInsensitiveDict()
headers["X-Yandex-API-Key"] = "a49c927e-27e2-4089-bf2e-0c865e207104"

mode = 'main'
pixels_count = 392
pixels = neopixel.NeoPixel(board.D18, 392, auto_write=False,)

bot = Bot(token=TOKEN)
dp = Dispatcher()

colors = {"❤️": "Красный", "🧡": "Оранжевый", "💛": "Желтый",
        "💚": "Синий", "💙": "Зеленый", "💜": "Оранжевый",
        "🖤": "Черный", "🤍": "Белый", "🤎": "Коричневый"}

rainbow = '🌈'
temperature = '🌡'

ind_colors = {0: "Красный", 1: "Оранжевый", 2: "Желтый",
            3: "Зеленый", 4: "Синий", 5: "Фиолетовый",
            6: "Черный", 7: "Белый", 8: "Коричневый"}

colors_ind = {}
for k, v in ind_colors.items():
    colors_ind[v] = k

# оранж (255, 165, 0)
rgb = {"Красный": (255, 0, 0), "Оранжевый": (251, 153, 2), "Желтый": (153, 153, 0),
        "Зеленый": (0, 255, 0), "Синий": (0, 0, 255), "Фиолетовый": (128, 0, 128),
        "Черный": (0, 0, 0), "Белый": (255, 255, 255), "Коричневый": (165, 42, 42)}


nums = {
    0: [ [1, 0], [2, 0], [3, 0], [4, 0], [5, 0], [6, 0] ],
    1: [ [1, 1], [6, 1] ],
    2: [ [2, 1], [1, 1], [7, 0], [4, 0], [5, 0] ],
    3: [ [2, 1], [1, 1], [7, 0], [6, 1], [5, 1] ],
    4: [ [3, 0], [7, 1], [1, 0], [6, 1] ],
    5: [ [2, 0], [3, 0], [7, 1], [6, 1], [5, 1] ],
    6: [ [2, 0], [2, 0], [3, 0], [4, 0], [5, 0], [6, 0], [7, 0] ],
    7: [ [2, 1], [1, 1], [6, 1] ],
    8: [ [1, 0], [2, 0], [3, 0], [4, 0], [5, 0], [6, 0], [7, 0] ],
    9: [ [7, 0], [3, 1], [2, 1], [1, 1], [6, 1], [5, 1] ]
}


char = {
    'С': [ [2, 0], [3, 0], [4, 0], [5, 0] ],
    '_': [ [5, 0] ],
    'Н': [ [3, 0], [4, 0], [7, 1], [1, 0], [6, 1] ],
    'Г': [ [2, 0], [3, 0], [4, 0] ],
    'о': [ [1, 0], [2, 0], [3, 0], [7, 1] ],
    '-': [ [7, 1] ],
    ' ': []
}

save_time = 0
save_countdown = 0
save_current_color = (0, 0, 0)
look = 0
pr = 0

last_request = {}
em = list(colors.keys())
em_kb = [types.KeyboardButton(text=i) for i in em]

builder = ReplyKeyboardBuilder()
for i in range(9):
    builder.add(em_kb[i])

builder.add(types.KeyboardButton(text=rainbow), types.KeyboardButton(text=temperature))

builder.adjust(3, 3, 3, 2)
general_kb = builder.as_markup(resize_keyboard=True)


def get_current_color():
    current_color = (0, 0, 0)

    with open('color.txt', 'r') as f:
        line = f.read()

        if len(line):
            l = line.split()
            current_color = (int(l[0]), int(l[1]), int(l[2]))

    return current_color


def set_current_color(color):
    with open('color.txt', 'w') as f:
        f.write(color)


async def change_symbol_opt(symbol_number, symbol, fast=False):
    global save_current_color

    current_color = get_current_color()
    save_current_color = current_color

    shift = 98 * (3 - symbol_number)

    for i in range(shift, shift + 98):
        pixels[i] = (0, 0, 0)
    pixels.show()

    blocks = []
    if symbol in nums:
        blocks = nums[symbol]
    elif symbol in char:
        blocks = char[symbol]
    else:
        print('ops')
        return

    for block in blocks:
        start = 0
        stop = 14
        step = 1

        if block[1] == 1:
            start = 13
            stop = -1
            step = -1

        for j in range(start, stop, step):
            pixels[shift + 14 * (block[0] - 1) + j] = current_color
            if not fast:
                pixels.show()
    if fast:
        pixels.show()


async def get_weather():
    print('get_weather')
    try:
        data = []
        with open('weather.txt', 'r') as f:
            for line in f:
                data.append(line)
        last_time = int(data[0])
        last_temp = data[1].replace('\n', '')

        #time_now = datetime.timestamp()
        dt = datetime.now()
        time_now = time.mktime(dt.timetuple())
        time_now = int(time_now)
        print(time_now)
        print(last_time)
        print(last_temp)
        temp = 0

        if time_now - last_time < 30*60:
            print('last')
            temp = last_temp
        else:
            print('new')
            resp = requests.get(url, headers=headers)

            resp = resp.json()
            print(resp)
            last_temp = resp['fact']['temp']
            last_temp = str(last_temp)

            with open('weather.txt', 'w') as f:
                f.write(str(time_now) + '\n')
                f.write(last_temp)

            temp = last_temp

        wait = 1
        print('temp', temp)
        temp = temp + 'оС'
        #for i in range(392):
        #    pixels[i] = (0, 0, 0)
        #pixels.show()
        if len(temp) < 4:
            temp = ' ' + temp
        for i in range(min(4, len(temp))):
            try:
                await change_symbol_opt(i, int(temp[i]))
            except Exception as e:
                await change_symbol_opt(i, temp[i])
    except Exception as e:
        print(e)


async def Wheel(WheelPos):
    if(WheelPos < 85):
        return (WheelPos * 3, 255 - WheelPos * 3, 0)
    elif(WheelPos < 170):
        WheelPos -= 85
        return (255 - WheelPos * 3, 0, WheelPos * 3)
    else:
        WheelPos -= 170
        return (0, WheelPos * 3, 255 - WheelPos * 3)


async def rainbowCycle(wait=1):
    for r in range(25):
        for g in range(25):
            for b in range(25):
                color = (r*10, g*10, b*10)
                for p in range(392):
                    pixels[p] = color
                print(color)
                pixels.show()
                await asyncio.sleep(wait)


'''
async def rainbowCycle(wait=0.002):
    for j in range(256):
        for i in range(392):
            pixels[i] = await Wheel((int(i * 256 / 392) + j) & 255)
        pixels.show()
        #await asyncio.sleep(wait)
'''


def get_countdown():
    dt_ny = datetime.strptime("1/1/23 00:00", "%d/%m/%y %H:%M")
    dt_now = datetime.now()
    dt = dt_ny - dt_now

    minutes = int(dt.total_seconds()) // 60
    hours = minutes // 60
    minutes %= 60
    print(hours, minutes)

    hours = str(hours)
    if len(hours) < 2:
        hours = '0' + hours

    minutes = str(minutes)
    if len(minutes) < 2:
        minutes = '0' + minutes

    time_str = hours + minutes

    return time_str


async def print_countdown():
    global save_countdown

    countdown_str = get_countdown()
    for i in range(4):
        await change_symbol_opt(i, int(countdown_str[i]))

    save_countdown = countdown_str


async def print_current_time():
    global save_time

    time_str = datetime.now().strftime('%H%M')
    print(time_str)

    for i in range(4):
        await change_symbol_opt(i, int(time_str[i]))

    save_time = time_str


async def print_current_year():
    time_str = datetime.now().strftime('%Y')
    for i in range(4):
        await change_symbol_opt(i, int(time_str[i]))


async def print_word(word):
    for i in range(len(word)):
        await change_symbol_opt(i, word[i])


async def all_black():
    global pixels_count
    for i in range(pixels_count):
        pixels[i] = (0, 0, 0)
    pixels.show()


async def timer():
    global save_time
    global save_countdown
    global save_current_color
    global mode

    wait = 5

    while True:
        year_str = datetime.now().strftime('%Y')
        new_current_color = get_current_color()
        time_str = datetime.now().strftime('%H%M')

        if mode == 'main':
            if time_str != save_time or save_current_color != new_current_color:
                await get_weather()
                await asyncio.sleep(5)

                await print_current_time()
                await asyncio.sleep(5)
        else:
            if save_current_color != new_current_color:
                await print_current_time()
                await asyncio.sleep(5)

                await get_weather()
                await asyncio.sleep(5)

                await print_current_year()
                await asyncio.sleep(5)

        await asyncio.sleep(wait)


async def start_bot():
    asyncio.ensure_future(timer())


@dp.message(Command('start'))
async def process_start_command(message):
    await message.reply("Привет!\nОтправляй мне эмодзи-сердечки и я буду менять цвет ленты в цвет отправленного сердечка",
        reply_markup=general_kb)


@dp.message(F.content_type=='text')
async def main_logic(msg):
    print(msg)
    global current_color
    global pr
    global mode
    global last_request

    if (msg.from_user.id in last_request) and (time.time() - last_request[msg.from_user.id] < 5.0):
        await msg.reply("Попробуй позже")
        return

    last_request[msg.from_user.id] = time.time()
    
    if msg.text == 'main':
        mode = 'main'
    elif msg.text == 'user':
        mode = 'user'
    elif len(msg.text) == 1 and msg.text >= '0' and msg.text <= '9':
        num = int(msg.text)
        #pr = num
        change_digit(num)

    elif msg.text in colors.keys():
        print("rgb", rgb[colors[msg.text]], rgb[colors[msg.text]][0])

        col = rgb[colors[msg.text]]
        current_color = str(col[0]) + ' ' + str(col[1]) + ' ' + str(col[2])
        with open('color.txt', 'w') as f:
            f.write(current_color)

        #await current_time()
    elif msg.text == rainbow:
        await rainbowCycle(2)

    elif msg.text == temperature:
        await get_weather()

    else:
        try:
            li = msg.text.split()
            print(li)
            mass = list(map(int, msg.text.split()))
            if len(mass) == 3 and mass[0] <= 255 and mass[1] <= 255 and mass[2] <= 255:
                current_color = str(mass[0]) + ' ' + str(mass[1]) + ' ' + str(mass[2])

                with open('color.txt', 'w') as f:
                    f.write(current_color)

                change(1)
        except Exception as e:
            print("oops")
        #for i in range(0, 100):
        #    pixels[i] = rgb[c]
        
    #await asyncio.sleep(5)
    look = 0
    try:
        await bot.send_message(248603604, '@' + msg.from_user.username + ' изменил цвет ' + msg.text)
    except Exception as e:
        print(e)
        await bot.send_message(248603604, '@' + msg.from_user.first_name + ' изменил цвет ' + msg.text)

    await msg.answer('Цвет изменен', reply_markup=general_kb)


async def st():
    dp.startup.register(start_bot)

    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(st())
    except Exception as e:
        print(e)
