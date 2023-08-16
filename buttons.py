from datetime import datetime

import pytz

from callbackFactory import ScalesCallbackFactory, PageCallbackFactory, ClearCallbackFactory
from aiogram.types import (InlineKeyboardMarkup,
                           InlineKeyboardButton,
                           KeyboardButton,
                           ReplyKeyboardMarkup)


def get_start_buttons() -> ReplyKeyboardMarkup:
    start_notify: KeyboardButton = KeyboardButton(text='Вкл. оповещения')
    stop_notify: KeyboardButton = KeyboardButton(text='Выкл. оповещения')

    create_scale: KeyboardButton = KeyboardButton(text='Добавить измерение')
    change_scale: KeyboardButton = KeyboardButton(text='Редактировать измерение')
    delete_scale: KeyboardButton = KeyboardButton(text='Удалить шкалу')

    show_scales: KeyboardButton = KeyboardButton(text='Показать информацию об измерениях')
    show_posts: KeyboardButton = KeyboardButton(text='Показать последние записи')

    return ReplyKeyboardMarkup(
        keyboard=[[start_notify, stop_notify],
                  [create_scale, change_scale, delete_scale],
                  [show_scales],
                  [show_posts]],
        resize_keyboard=True,
        one_time_keyboard=True
    )


def get_key_board_scales(scales, old_text=None, cb: ScalesCallbackFactory = None):
    inline_keyboard = []
    text = ''
    now = datetime.now()
    current_year = cb.year if cb else now.year
    current_month = cb.month if cb else now.month
    current_day = cb.day if cb else now.day
    current_hour = cb.hour if cb else now.hour
    for scale in scales:
        line = []
        if cb and int(scale['id']) == cb.scale_id:
            continue
        if old_text and scale['title'] not in old_text:
            continue
        if scale['type'] == 'range':
            title = scale['title']
            for i in range(5):
                line.append(InlineKeyboardButton(
                    text=f"{title} = 1" if i == 0 else f"{i + 1}{'ㅤ' * 3}",
                    callback_data=ScalesCallbackFactory(
                        scale_id=int(scale['id']),
                        scale_value=i + 1,
                        year=current_year,
                        month=current_month,
                        day=current_day,
                        hour=current_hour).pack(),
                ))
        else:
            line.append(InlineKeyboardButton(
                text=f"{scale['title']} - True",
                callback_data=ScalesCallbackFactory(
                    scale_id=int(scale['id']),
                    scale_value=1,
                    year=current_year,
                    month=current_month,
                    day=current_day,
                    hour=current_hour).pack(),
            ))
            line.append(InlineKeyboardButton(
                text=f"{scale['title']} - False",
                callback_data=ScalesCallbackFactory(
                    scale_id=int(scale['id']),
                    scale_value=0,
                    year=current_year,
                    month=current_month,
                    day=current_day,
                    hour=current_hour).pack(),
            ))
        text += f"{scale['title']}\n"

        inline_keyboard.append(line)
    clear_btn = InlineKeyboardButton(text='Не отмечать этот час',
                                     callback_data=ClearCallbackFactory().pack())
    inline_keyboard.append([clear_btn])
    return text, InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def post_pagination_buttons(response):
    btn_list = []
    if not response:
        return [[]]
    if response['previous']:
        link = response['next']
        try:
            page_count = link.split('?')[1].replace('page=', '')
        except AttributeError:
            page_count = 0
        prev_btn = InlineKeyboardButton(text='prev page',
                                        callback_data=PageCallbackFactory(
                                            page_count=int(page_count), ).pack(), )
        btn_list.append(prev_btn)
    if response['next']:
        link = response['next']
        page_count = link.split('?')[1].replace('page=', '')
        print(page_count)
        next_btn = InlineKeyboardButton(text='next page',
                                        callback_data=PageCallbackFactory(
                                            page_count=int(page_count), ).pack())
        btn_list.append(next_btn)
    return InlineKeyboardMarkup(inline_keyboard=[btn_list])
