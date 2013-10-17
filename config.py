import os

APP_KEY= ''
APP_SECRET = ''
REDIRECT_URL = ''
PATH = os.path.dirname(os.path.abspath(__file__))
TOKEN_FILE = os.path.join(PATH, 'token.json')
ACCESS_TOKEN = ''
proxies = {}
