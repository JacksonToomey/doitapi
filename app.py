from wsgicors import CORS
from factory import create_app


app = CORS(create_app(), headers='*', methods='*', origin='*')
