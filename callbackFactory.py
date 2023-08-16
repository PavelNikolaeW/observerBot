from datetime import datetime

from aiogram.filters.callback_data import CallbackData


class ScalesCallbackFactory(CallbackData, prefix='scale'):
    scale_id: int
    scale_value: int
    year: int
    month: int
    hour: int
    day: int


class ClearCallbackFactory(CallbackData, prefix='clear'):
    pass


class PageCallbackFactory(CallbackData, prefix='page'):
    page_count: int
