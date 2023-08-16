from aiogram import types
from aiogram.filters import Text

from main import dp, data


@dp.message(Text(text="Показать информацию об измерениях"))
async def show_info_scales(message):
    global data
    nik = f'@{message.chat.username}'.lower()
    text = ''
    for scale in data[nik]['scales']:
        text += '\n'
        for key, val in scale.items():
            if key != 'id':
                text += f'{key}: {val}\n'
    await message.answer(text=text)


@dp.message(Text(text='Добавить измерение'))
async def create_scale(message: types.Message):
    template = """
    /create_scale
    название: (название шаклы)
    описание: (опишите что означает каждая из оценок)
    тип: (range или bool)

    тип range это шкала от 1 до 5
    тип bool это шкала да / нет
    название, описание и тип пишите с новой строки, не забывайте про <:> 
    """
    await message.answer(text=f"Отправьте следующий шаблон\n {template}")
