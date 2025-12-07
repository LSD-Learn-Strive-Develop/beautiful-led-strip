from aiogram import F, Router, types
from aiogram.filters import Command
import time
from bot.keyboards import get_main_kb
import led
from main import bot
import symbols

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.reply("Привет!\nОтправляй мне эмодзи-сердечки и я буду менять цвет ленты в цвет отправленного сердечка", 
                         reply_markup=get_main_kb())


@router.message(F.text)
async def main_logic(msg: types.Message):

    if (msg.from_user.id in led.last_request) and (time.time() - led.last_request[msg.from_user.id] < 5.0):
        await msg.reply("Попробуй позже")
        return

    led.last_request[msg.from_user.id] = time.time()
    
    if msg.text in ['main', 'user', 'fight']:
        led.mode = msg.text

    elif msg.text in symbols.colors.keys():
        col = symbols.rgb[symbols.colors[msg.text]]
        print("rgb", col, col[0])
        led.current_color = str(col[0]) + ' ' + str(col[1]) + ' ' + str(col[2])
        with open('/home/romanychev/dev/beautiful-led-strip/color.txt', 'w') as f:
            f.write(led.current_color)
        led.show_item = 1

    elif msg.text == symbols.rainbow:
        led.show_item = 2

    elif msg.text == symbols.temperature:
        led.show_item = 3

    else:
        admins = [666789860, 839982378, 1140559982, 1045138384, 379698720, 5298518984, 758017709, 248603604, 356384042, 718868214, 355825999, 446574710, 724536101, 405629002]
        try:
            flag_s = 0
            
            for ch in msg.text:
                print(ch)
                if not ch in symbols.chars.keys() and not ch in symbols.special_chars.keys():
                    print('OK')
                    flag_s = 1
            

            print(msg.from_user.id)
            if msg.from_user.id in admins and flag_s == 0:
                led.show_item = msg.text
        except Exception as e:
            print("oops")

    try:
        await bot.send_message(248603604, '@' + msg.from_user.username + ' изменил цвет ' + msg.text)
    except Exception as e:
        print(e)
        await bot.send_message(248603604, '@' + msg.from_user.first_name + ' изменил цвет ' + msg.text)

    await msg.answer('Цвет изменен', reply_markup=general_kb)