import math
from typing import Dict

try:
    from app.data.common_passwords import COMMON_PASSWORDS_LIST
except ImportError:
    COMMON_PASSWORDS_LIST = []

ATTACK_SCENARIOS = {
    "online_throttled": {
        "speed": 100,
        "name": "Онлайн-атака с блокировкой",
        "description": "Атака с ограничением попыток (100 хешей/сек)"
    },
    "online_no_throttle": {
        "speed": 10000,
        "name": "Онлайн-атака без блокировки",
        "description": "Атака без ограничения попыток (10K хешей/сек)"
    },
    "offline_slow_hash": {
        "speed": 10000,
        "name": "Offline: bcrypt/Argon2",
        "description": "Оффлайн-атака на медленные хеши (1 GPU, 10K хешей/сек)"
    },
    "offline_fast_hash": {
        "speed": 100000000000,
        "name": "Offline: MD5/SHA1",
        "description": "Оффлайн-атака на быстрые хеши (GPU-ферма, 100B хешей/сек)"
    }
}


def format_time(seconds: float) -> str:
    if seconds < 1:
        return "мгновенно"
    elif seconds < 60:
        return f"{int(seconds)} секунд"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes} минут"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"{hours} часов"
    elif seconds < 31536000:
        days = int(seconds / 86400)
        return f"{days} дней"
    elif seconds < 31536000 * 100:
        years = int(seconds / 31536000)
        return f"{years} лет"
    elif seconds < 31536000 * 1e6:
        thousands = int(seconds / (31536000 * 1000))
        return f"{thousands} тысяч лет"
    elif seconds < 31536000 * 1e9:
        millions = int(seconds / (31536000 * 1e6))
        return f"{millions} миллионов лет"
    elif seconds < 31536000 * 1e12:
        billions = int(seconds / (31536000 * 1e9))
        return f"{billions} миллиардов лет"
    else:
        return "практически невозможно (тепловая смерть вселенной)"


def estimate_crack_time(password: str, analysis: Dict) -> Dict:
    if analysis["details"]["is_common"]:
        pwd_lower = password.lower()
        try:
            position = COMMON_PASSWORDS_LIST.index(pwd_lower) + 1
            guesses = position
        except (ValueError, AttributeError):
            guesses = 1000
    else:
        effective_entropy = analysis.get("effective_entropy", analysis["entropy_bits"])
        guesses = 2 ** effective_entropy

    crack_times = {}
    for scenario_key, scenario_data in ATTACK_SCENARIOS.items():
        speed = scenario_data["speed"]
        seconds = guesses / speed
        crack_times[scenario_key] = {
            "name": scenario_data["name"],
            "description": scenario_data["description"],
            "seconds": seconds,
            "display": format_time(seconds)
        }

    return {
        "guesses": guesses,
        "crack_times": crack_times
    }