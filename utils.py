import hashlib
import json
import random
import re
import secrets
import string
from datetime import datetime, timedelta
from pathlib import Path

from config import COMMON_PASSWORDS_FILE, DATA_FILE

SPECIAL_CHARS = "!@#$%^&*()-_=+[]{};:,.?/"

def load_common_passwords() -> set[str]:
    path = Path(COMMON_PASSWORDS_FILE)
    if not path.exists():
        return {
            "123456", "password", "qwerty", "admin", "123123",
            "111111", "password1", "qwerty123", "000000", "abc123"
        }
    with path.open("r", encoding="utf-8") as f:
        return {line.strip() for line in f if line.strip()}


COMMON_PASSWORDS = load_common_passwords()


def load_data() -> list[dict]:
    path = Path(DATA_FILE)
    if not path.exists():
        return []
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def save_data(data: list[dict]) -> None:
    with Path(DATA_FILE).open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def password_exists(password: str, data: list[dict]) -> bool:
    hashed = hash_password(password)
    return any(item["password_hash"] == hashed for item in data)


def generate_password(
    length: int,
    use_lower: bool,
    use_upper: bool,
    use_digits: bool,
    use_symbols: bool,
    data: list[dict],
    max_attempts: int = 5000,
) -> str:
    pools = []
    required_chars = []

    if use_lower:
        pools.append(string.ascii_lowercase)
        required_chars.append(secrets.choice(string.ascii_lowercase))
    if use_upper:
        pools.append(string.ascii_uppercase)
        required_chars.append(secrets.choice(string.ascii_uppercase))
    if use_digits:
        pools.append(string.digits)
        required_chars.append(secrets.choice(string.digits))
    if use_symbols:
        pools.append(SPECIAL_CHARS)
        required_chars.append(secrets.choice(SPECIAL_CHARS))

    if not pools:
        raise ValueError("Нужно выбрать хотя бы один набор символов.")

    if length < len(required_chars):
        raise ValueError("Длина пароля меньше числа обязательных категорий символов.")

    all_chars = "".join(pools)

    for _ in range(max_attempts):
        password_chars = required_chars.copy()
        while len(password_chars) < length:
            password_chars.append(secrets.choice(all_chars))
        random.SystemRandom().shuffle(password_chars)
        pwd = "".join(password_chars)

        if pwd.lower() in COMMON_PASSWORDS or pwd in COMMON_PASSWORDS:
            continue
        if password_exists(pwd, data):
            continue
        return pwd

    raise RuntimeError("Не удалось сгенерировать уникальный пароль.")


def password_score(password: str) -> int:
    pwd_lower = password.lower()
    if pwd_lower in COMMON_PASSWORDS or password in COMMON_PASSWORDS:
        return 0

    score = 0

    if len(password) >= 8:
        score += 2
    if len(password) >= 12:
        score += 2

    if re.search(r"[a-z]", password):
        score += 1
    if re.search(r"[A-Z]", password):
        score += 1
    if re.search(r"\d", password):
        score += 2
    if re.search(rf"[{re.escape(SPECIAL_CHARS)}]", password):
        score += 2

    unique_ratio = len(set(password)) / len(password) if password else 0
    if unique_ratio > 0.7:
        score += 1

    return min(score, 10)


def evaluate_password(password: str) -> dict:
    score = 0
    advice = []

    if len(password) >= 12:
        score += 2
    else:
        advice.append("Увеличьте длину пароля до 12+ символов")

    if re.search(r"[a-z]", password):
        score += 1
    else:
        advice.append("Добавьте строчные буквы")

    if re.search(r"[A-Z]", password):
        score += 1
    else:
        advice.append("Добавьте заглавные буквы")

    if re.search(r"\d", password):
        score += 1
    else:
        advice.append("Добавьте цифры")

    if re.search(rf"[{re.escape(SPECIAL_CHARS)}]", password):
        score += 2
    else:
        advice.append("Добавьте спецсимволы")

    if password.lower() in COMMON_PASSWORDS or password in COMMON_PASSWORDS:
        score = 0
        advice.insert(0, "Этот пароль входит в список распространённых слабых паролей")

    strength = "Низкая" if score < 3 else "Средняя" if score < 5 else "Высокая"

    return {"strength": strength, "score": min(score, 10), "advice": advice}


def score_label(score: int) -> str:
    if score <= 3:
        return "Слабый"
    if score <= 6:
        return "Средний"
    if score <= 8:
        return "Хороший"
    return "Сильный"


def score_color(score: int) -> str:
    if score <= 3:
        return "#ef4444"
    if score <= 6:
        return "#f59e0b"
    if score <= 8:
        return "#22c55e"
    return "#10b981"


def save_password_entry(name: str, password: str, days: int) -> None:
    data = load_data()
    expire_date = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
    data.append({
        "id": secrets.token_hex(8),
        "name": name,
        "password_hash": hash_password(password),
        "password_plain": password,
        "expire": expire_date,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    })
    save_data(data)


def delete_password_entry(entry_id: str) -> None:
    data = load_data()
    data = [item for item in data if item["id"] != entry_id]
    save_data(data)


def get_passwords_view(search: str | None = None) -> list[dict]:
    data = load_data()
    result = []

    for item in data:
        if search and search.lower() not in item["name"].lower():
            continue

        expire_dt = datetime.strptime(item["expire"], "%Y-%m-%d")
        expired = datetime.now() > expire_dt

        result.append({
            **item,
            "status": "EXPIRED" if expired else "OK",
            "expired": expired,
        })

    result.sort(key=lambda x: x["name"].lower())
    return result