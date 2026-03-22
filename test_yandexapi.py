import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("YANDEX_API_KEY")
FOLDER_ID = os.getenv("YANDEX_FOLDER_ID")

url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"

headers = {
    "Authorization": f"Api-Key {API_KEY}",
    "Content-Type": "application/json",
}

payload = {
    "modelUri": f"gpt://{FOLDER_ID}/yandexgpt-lite",
    "completionOptions": {
        "stream": False,
        "temperature": 0.2,
        "maxTokens": 50
    },
    "messages": [
        {"role": "user", "text": "Напиши слово: тест"}
    ]
}

response = requests.post(url, headers=headers, json=payload, timeout=20)
print("STATUS:", response.status_code)
print(response.text)