from aiogram.utils.keyboard import ReplyKeyboardBuilder
from symbols import colors, rainbow, temperature


def get_main_kb():
    builder = ReplyKeyboardBuilder()
    em = list(colors.keys())
    
    for el in em:
        builder.button(text=el)
    builder.button(text=rainbow)
    builder.button(text=temperature)
    builder.adjust(3, 3, 3, 2)

    return builder.as_markup(resize_keyboard=True)
