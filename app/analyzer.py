import math
import string
from typing import Dict, List, Set, Tuple

try:
    from app.data.keyboard_patterns import KEYBOARD_NEIGHBORS, COMMON_KEYBOARD_WALKS
except ImportError:
    KEYBOARD_NEIGHBORS = {}
    COMMON_KEYBOARD_WALKS = []

try:
    from app.data.common_passwords import COMMON_PASSWORDS
except ImportError:
    COMMON_PASSWORDS = set()

try:
    from app.data.wordlist_eff import WORDLIST
except ImportError:
    WORDLIST = []

LEET_REVERSE_MAP = {
    '@': 'a', '4': 'a',
    '3': 'e',
    '1': 'i', '!': 'i',
    '0': 'o',
    '$': 's', '5': 's',
    '7': 't',
    '+': 't',
    '8': 'b',
    '9': 'g',
    '6': 'g',
    '2': 'z'
}


def calculate_charset_size(password: str) -> Tuple[int, bool, bool, bool, bool]:
    has_lower = any(c in string.ascii_lowercase for c in password)
    has_upper = any(c in string.ascii_uppercase for c in password)
    has_digit = any(c in string.digits for c in password)
    has_symbol = any(c in string.punctuation for c in password)

    charset_size = 0
    if has_lower:
        charset_size += 26
    if has_upper:
        charset_size += 26
    if has_digit:
        charset_size += 10
    if has_symbol:
        charset_size += 32

    has_unicode = any(ord(c) > 127 for c in password)
    if has_unicode:
        charset_size += 100

    return charset_size, has_lower, has_upper, has_digit, has_symbol


def detect_repeats(password: str) -> float:
    penalty = 0.0
    pwd_lower = password.lower()

    i = 0
    while i < len(pwd_lower):
        char = pwd_lower[i]
        count = 1
        while i + count < len(pwd_lower) and pwd_lower[i + count] == char:
            count += 1
        if count >= 3:
            penalty += count * 2
        i += count

    for block_len in range(2, len(pwd_lower) // 2 + 1):
        for start in range(len(pwd_lower) - block_len * 2 + 1):
            block = pwd_lower[start:start + block_len]
            next_block = pwd_lower[start + block_len:start + block_len * 2]
            if block == next_block:
                penalty += block_len * 3
                break

    return penalty


def detect_sequences(password: str) -> float:
    penalty = 0.0
    pwd_lower = password.lower()
    for seq_len in range(3, len(pwd_lower) + 1):
        for start in range(len(pwd_lower) - seq_len + 1):
            seq = pwd_lower[start:start + seq_len]

            is_ascending = True
            is_descending = True

            for i in range(1, len(seq)):
                if ord(seq[i]) != ord(seq[i - 1]) + 1:
                    is_ascending = False
                if ord(seq[i]) != ord(seq[i - 1]) - 1:
                    is_descending = False

            if is_ascending or is_descending:
                penalty += seq_len * 2
                break

    return penalty


def detect_keyboard_patterns(password: str) -> float:
    penalty = 0.0
    pwd_lower = password.lower()

    for pattern in COMMON_KEYBOARD_WALKS:
        if pattern in pwd_lower:
            penalty += len(pattern) * 3

    if KEYBOARD_NEIGHBORS:
        for i in range(len(pwd_lower) - 2):
            path_len = 1
            for j in range(i, len(pwd_lower) - 1):
                char = pwd_lower[j]
                next_char = pwd_lower[j + 1]
                if next_char in KEYBOARD_NEIGHBORS.get(char, set()):
                    path_len += 1
                else:
                    break
            if path_len >= 3:
                penalty += path_len * 2

    return penalty


def detect_common_passwords(password: str) -> Tuple[float, bool, int]:
    pwd_lower = password.lower()

    if pwd_lower in COMMON_PASSWORDS:
        return 100.0, True, 1

    for suffix_len in range(1, 5):
        if pwd_lower[-suffix_len:].isdigit():
            base = pwd_lower[:-suffix_len]
            if base in COMMON_PASSWORDS:
                return 50.0, True, 100

    decoded = pwd_lower
    for leet, normal in LEET_REVERSE_MAP.items():
        decoded = decoded.replace(leet, normal)

    if decoded != pwd_lower and decoded in COMMON_PASSWORDS:
        return 40.0, True, 200

    return 0.0, False, 0


def detect_dictionary_words(password: str) -> float:
    penalty = 0.0
    pwd_lower = password.lower()

    if not WORDLIST:
        return penalty

    dict_words = {w for w in WORDLIST if len(w) >= 4}

    for length in range(4, min(21, len(pwd_lower) + 1)):
        for start in range(len(pwd_lower) - length + 1):
            substring = pwd_lower[start:start + length]
            if substring in dict_words:
                penalty += length * 1.5

    return penalty


def detect_leet_speak(password: str) -> float:
    penalty = 0.0
    pwd_lower = password.lower()

    leet_count = sum(1 for c in pwd_lower if c in LEET_REVERSE_MAP)

    if leet_count == 0:
        return penalty

    decoded = pwd_lower
    for leet, normal in LEET_REVERSE_MAP.items():
        decoded = decoded.replace(leet, normal)

    if WORDLIST and decoded in WORDLIST:
        penalty += leet_count * 5

    return penalty


def analyze_password(password: str) -> Dict:
    if not password:
        return {
            "score": 0,
            "entropy_bits": 0.0,
            "crack_time_display": "мгновенно",
            "warnings": ["Пароль пуст"],
            "suggestions": ["Введите пароль"],
            "details": {
                "length": 0,
                "charset_size": 0,
                "has_upper": False,
                "has_lower": False,
                "has_digit": False,
                "has_symbol": False,
                "repeat_penalty": 0.0,
                "sequence_penalty": 0.0,
                "keyboard_penalty": 0.0,
                "dictionary_penalty": 0.0,
                "is_common": False
            }
        }

    length = len(password)
    charset_size, has_lower, has_upper, has_digit, has_symbol = calculate_charset_size(password)
    entropy_bits = length * math.log2(charset_size) if charset_size > 0 else 0

    repeat_penalty = detect_repeats(password)
    sequence_penalty = detect_sequences(password)
    keyboard_penalty = detect_keyboard_patterns(password)
    common_penalty, is_common, common_position = detect_common_passwords(password)
    dictionary_penalty = detect_dictionary_words(password)
    leet_penalty = detect_leet_speak(password)

    total_penalty = (repeat_penalty + sequence_penalty + keyboard_penalty +
                     common_penalty + dictionary_penalty + leet_penalty)

    effective_entropy = max(0, entropy_bits - total_penalty)

    if is_common:
        score = 0
    elif effective_entropy < 28:
        score = 0
    elif effective_entropy < 36:
        score = 1
    elif effective_entropy < 60:
        score = 2
    elif effective_entropy < 100:
        score = 3
    else:
        score = 4

    warnings = []
    suggestions = []

    if repeat_penalty > 0:
        warnings.append("Содержит повторяющиеся символы или блоки")
    if sequence_penalty > 0:
        warnings.append("Содержит последовательности (1234, abcd)")
    if keyboard_penalty > 0:
        warnings.append("Содержит клавиатурный паттерн (qwerty, asdf)")
    if is_common:
        warnings.append("Является частым паролем или его вариацией")
    if dictionary_penalty > 0:
        warnings.append("Содержит словарные слова")
    if leet_penalty > 0:
        warnings.append("Использует предсказуемые leet-speak замены")

    if not has_upper:
        suggestions.append("Добавьте заглавные буквы")
    if not has_lower:
        suggestions.append("Добавьте строчные буквы")
    if not has_digit:
        suggestions.append("Добавьте цифры")
    if not has_symbol:
        suggestions.append("Добавьте спецсимволы")
    if length < 12:
        suggestions.append("Увеличьте длину до 12+ символов")
    elif length < 16:
        suggestions.append("Для надёжности увеличьте длину до 16+ символов")

    return {
        "score": score,
        "entropy_bits": round(entropy_bits, 1),
        "effective_entropy": round(effective_entropy, 1),
        "crack_time_display": "",
        "warnings": warnings,
        "suggestions": suggestions,
        "details": {
            "length": length,
            "charset_size": charset_size,
            "has_upper": has_upper,
            "has_lower": has_lower,
            "has_digit": has_digit,
            "has_symbol": has_symbol,
            "repeat_penalty": round(repeat_penalty, 2),
            "sequence_penalty": round(sequence_penalty, 2),
            "keyboard_penalty": round(keyboard_penalty, 2),
            "dictionary_penalty": round(dictionary_penalty, 2),
            "is_common": is_common
        }
    }