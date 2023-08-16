import logging
import requests

from buttons import get_start_buttons, post_pagination_buttons
from constants import SCALE_FIELDS, host, api, default_headers
from custom_exceptions import APIException
from main import data


async def get_profile(nik, message):
    global data
    profile = data.get(nik)
    if profile:
        return profile
    try:
        profile = request_api(f'observer/data/{nik}/', 'GET')
        data[nik] = profile
        return profile
    except APIException:
        await message.answer(
            'Ваш профиль не найден, зарегистрируйте ваш телеграм на сайте и добавьте то что'
            ' хотите отслеживать https://problem-solving-framework.ru/observation/')


async def set_chat_id(nik, message, chat_id=None):
    global data
    try:
        res = request_api(f'observer/data/{nik}/', 'PATCH', {'chat_id': chat_id})
        scales = res.get('scales')
        data[nik] = res
        print(res)
        if len(scales) > 0:
            await message.answer("Добро пожаловать, я буду присылать напоминания",
                                 reply_markup=get_start_buttons())
            return True
        else:
            await message.answer(
                "Добавьте информацию о том, что хотите отслеживать "
                "https://problem-solving-framework.ru/observation/")
    except APIException:
        await message.answer(f'Произошла ошибка на сервере, уже чиним')


def request_api(end_point='', method='GET', body=None, add_headers=None) -> dict:
    url = f'{host}{api}{end_point}'
    headers = default_headers.copy()
    if add_headers is not None:
        headers.update(add_headers)
    response = requests.request(url=url, method=method, headers=headers, json=body)
    print(method, url, body, response.status_code)
    if response.status_code >= 400:
        logging.error(response.status_code)
        raise APIException(response.status_code)
    try:
        return response.json()
    except Exception as e:
        return {'status_code': response.status_code}


def scale_create_validator(args):
    if not args:
        raise Exception(f'Не введена информация')
    body = {}
    for field in args.split('\n'):
        try:
            key, val = field.split(':', 1)
        except Exception as e:
            raise Exception(f'Ошибка парсинга строки нет < : >')
        key = key.strip()
        val = val.strip()
        if key not in SCALE_FIELDS.keys():
            raise Exception(f'Не допустимое поля <{key}>\nдопустимые поля: <{SCALE_FIELDS.keys()}>')
        if len(val) < 3:
            raise Exception(f'Значение поля слишком короткое <{val}>')
        if len(val) > 300:
            raise Exception(f'Значение поля слишком длинное <{val}> макс. длинна 300 символов')
        body[SCALE_FIELDS[key]] = val
    if len(body.keys()) != len(SCALE_FIELDS.keys()):
        raise Exception(f'Не все поля заполнены. Пропущено {SCALE_FIELDS.values() - body.keys()}')
    return body


def scale_update_validator(args, scales):
    if not args:
        raise Exception(f'Не введена информация')
    print(args)
    try:
        title, field_text = args.split(' ', 1)
    except Exception as e:
        raise Exception(f'Ошибка парсинга строки нет пробелов')
    try:
        field, text = field_text.split(':', 1)
    except Exception as e:
        raise Exception(f'Ошибка парсинга строки нет < : >')
    field = field.strip(' ')
    text = text.strip(' ')
    id = [scale['id'] for scale in scales if scale['title'] == title.strip(' ')]
    if len(id) == 0:
        raise Exception(f'Указанная шкала не найдена {title}')
    if field not in SCALE_FIELDS.keys():
        raise Exception(f'Неверное введено поле {field}')
    if len(text) < 3:
        raise Exception(f'Текст слишком короткий {text}')
    if len(text) > 300:
        raise Exception(f"Текст слишком длинный макс. длинна 300 символов")

    return id[0], {SCALE_FIELDS[field]: text}


if __name__ == '__main__':
    print(request_api(f'observer/data/@unikalnynik/', 'PATCH', {'is_active': False}))
