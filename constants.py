import os

from dotenv import load_dotenv

load_dotenv()
host = os.getenv('HOST')
api = 'api/v1/'

default_headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Token {os.getenv("ADMIN_TOKEN")}'
}

SCALE_FIELDS = {'название': 'title', 'тип': 'type', 'описание': 'description'}