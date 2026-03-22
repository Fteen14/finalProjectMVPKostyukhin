import requests
from config import YANDEX_API_KEY, YANDEX_FOLDER_ID

YANDEX_GPT_URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"


def _ask_yandex_gpt(prompt: str) -> str:
    if not YANDEX_API_KEY or not YANDEX_FOLDER_ID:
        return "AI недоступен: не заданы YANDEX_API_KEY или YANDEX_FOLDER_ID в .env"

    headers = {
        "Authorization": f"Api-Key {YANDEX_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "modelUri": f"gpt://{YANDEX_FOLDER_ID}/yandexgpt-lite",
        "completionOptions": {
            "stream": False,
            "temperature": 0.4,
            "maxTokens": 700,
        },
        "messages": [
            {
                "role": "system",
                "text": "Ты помощник по анализу безопасности паролей. Отвечай кратко, по делу и на русском языке."
            },
            {
                "role": "user",
                "text": prompt
            }
        ]
    }

    try:
        response = requests.post(
            YANDEX_GPT_URL,
            headers=headers,
            json=payload,
            timeout=20
        )
        response.raise_for_status()
        data = response.json()
        return data["result"]["alternatives"][0]["message"]["text"]
    except requests.RequestException as e:
        return f"Ошибка запроса к YandexGPT: {e}"
    except (KeyError, IndexError, TypeError):
        return "Ошибка обработки ответа YandexGPT."


def analyze_password_ai(password: str) -> str:
    prompt = f"""
Проанализируй пароль: {password}

Нужно:
1. Кратко оценить уровень безопасности.
2. Объяснить слабые места.
3. Дать 3 рекомендации по улучшению.

Ответ оформи кратко, списком.
"""
    return _ask_yandex_gpt(prompt)


def improve_password_ai(password: str) -> str:
    prompt = f"""
Улучши пароль: {password}

Требования:
- длина 12-16 символов
- использовать строчные и заглавные буквы
- использовать цифры
- использовать спецсимволы
- пароль должен быть удобен для учебного примера

Верни только один новый пароль, без пояснений и без кавычек.
"""
    return _ask_yandex_gpt(prompt).strip()