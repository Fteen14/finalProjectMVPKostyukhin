import os
from dotenv import load_dotenv

load_dotenv()

APP_USER = os.getenv("APP_USER", "user")
APP_PASSWORD = os.getenv("APP_PASSWORD", "password")
SECRET_KEY = os.getenv("SECRET_KEY", "change_me")

YANDEX_API_KEY = os.getenv("YANDEX_API_KEY", "")
YANDEX_FOLDER_ID = os.getenv("YANDEX_FOLDER_ID", "")

DATA_FILE = os.getenv("DATA_FILE", "passwords.json")
COMMON_PASSWORDS_FILE = os.getenv("COMMON_PASSWORDS_FILE", "common_passwords.txt")