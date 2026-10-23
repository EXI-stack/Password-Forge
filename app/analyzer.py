import math
import string
from collections import Counter
from typing import Dict, Tuple

try:
    from app.data.keyboard_patterns import KEYBOARD_NEIGHBORS, COMMON_KEYBOARD_WALKS
except ImportError:
    KEYBOARD_NEIGHBORS = {}
    COMMON_KEYBOARD_WALKS = [
        "qwerty", "qwertyuiop", "asdf", "asdfghjkl", "zxcv", "zxcvbnm",
        "1234567890", "qazwsx", "1qaz2wsx"
    ]

try:
    from app.data.common_passwords import COMMON_PASSWORDS
except ImportError:
    COMMON_PASSWORDS = set()

try:
    from app.data.wordlist_eff import WORDLIST
except ImportError:
    from app.generator import WORDLIST

LEET_REVERSE_MAP = {
    '@': 'a', '4': 'a',
    '3': 'e',
    '1': 'i', '!': 'i',
    '0': 'o',
    '$': 's', '5': 's',
    '7': 't', '+': 't',
    '8': 'b',
    '9': 'g', '6': 'g',
    '2': 'z'
}

DICT_WORDS_SET = {w.lower() for w in WORDLIST if len(w) >= 4}
WORDLIST_ENTROPY_BITS = math.log2(max(len(WORDLIST), 7776)) if WORDLIST else 12.92


def calculate_charset_size(password: str) -> Tuple[int, bool, bool, bool, bool]:
    has_ascii_lower = any(c in string.ascii_lowercase for c in password)
    has_ascii_upper = any(c in string.ascii_uppercase for c in password)
    has_unicode_lower = any(ord(c) > 127 and c.islower() for c in password)
    has_unicode_upper = any(ord(c) > 127 and c.isupper() for c in password)

    has_lower = has_ascii_lower or has_unicode_lower
    has_upper = has_ascii_upper or has_unicode_upper
    has_digit = any(c in string.digits for c in password)
    has_symbol = any((c in string.punctuation or c == ' ') for c in password)

    charset_size = 0
    if has_ascii_lower:
        charset_size += 26
    if has_ascii_upper:
        charset_size += 26
    if has_unicode_lower:
        charset_size += 33
    if has_unicode_upper:
        charset_size += 33
    if has_digit:
        charset_size += 10
    if has_symbol:
        charset_size += 33 if ' ' in password else 32

    has_other_unicode = any(ord(c) > 127 and not c.isalpha() for c in password)
    if has_other_unicode:
        charset_size += 50

    return charset_size, has_lower, has_upper, has_digit, has_symbol


def detect_repeats(password: str, char_entropy: float) -> float:
    penalty = 0.0
    pwd_lower = password.lower()
    n = len(pwd_lower)
    covered = [False] * n
    i = 0
    while i < n:
        char = pwd_lower[i]
        count = 1
        while i + count < n and pwd_lower[i + count] == char:
            count += 1
        if count >= 3:
            penalty += (count - 1) * char_entropy * 0.85
            for k in range(i, i + count):
                covered[k] = True
        i += count

    for block_len in range(n // 2, 1, -1):
        i = 0
        while i <= n - block_len * 2:
            if any(covered[i:i + block_len * 2]):
                i += 1
                continue
            block = pwd_lower[i:i + block_len]
            repeats = 1
            while (i + (repeats + 1) * block_len <= n and
                   pwd_lower[i + repeats * block_len:i + (repeats + 1) * block_len] == block):
                repeats += 1
            if repeats >= 2:
                repeated_chars = (repeats - 1) * block_len
                penalty += repeated_chars * char_entropy * 0.8
                for k in range(i, i + repeats * block_len):
                    covered[k] = True
                i += repeats * block_len
            else:
                i += 1

    non_alnum_counts = Counter(
        pwd_lower[idx] for idx in range(n)
        if not covered[idx] and not pwd_lower[idx].isalnum()
    )
    for _, count in non_alnum_counts.items():
        if count >= 2:
            penalty += (count - 1) * char_entropy * 0.85

    return penalty


def detect_sequences(password: str, char_entropy: float) -> float:
    penalty = 0.0
    pwd_lower = password.lower()
    n = len(pwd_lower)
    if n < 3:
        return 0.0

    i = 0
    while i < n - 2:
        if not (pwd_lower[i].isalnum() and pwd_lower[i + 1].isalnum()):
            i += 1
            continue

        diff = ord(pwd_lower[i + 1]) - ord(pwd_lower[i])
        if diff in (1, -1):
            run_len = 2
            while (i + run_len < n and
                   pwd_lower[i + run_len].isalnum() and
                   ord(pwd_lower[i + run_len]) - ord(pwd_lower[i + run_len - 1]) == diff):
                run_len += 1

            if run_len >= 3:
                penalty += (run_len - 1) * char_entropy * 0.8
                i += run_len
                continue
        i += 1

    return penalty


def detect_keyboard_patterns(password: str, char_entropy: float) -> float:
    penalty = 0.0
    pwd_lower = password.lower()
    n = len(pwd_lower)
    if n < 3:
        return 0.0

    covered = [False] * n
    walks = sorted(
        set(COMMON_KEYBOARD_WALKS) | {w[::-1] for w in COMMON_KEYBOARD_WALKS},
        key=len,
        reverse=True
    )

    for pattern in walks:
        plen = len(pattern)
        if plen < 3 or plen > n:
            continue
        start = 0
        while True:
            idx = pwd_lower.find(pattern, start)
            if idx == -1:
                break
            if not any(covered[idx:idx + plen]):
                penalty += (plen - 1) * char_entropy * 0.8
                for k in range(idx, idx + plen):
                    covered[k] = True
            start = idx + 1

    if KEYBOARD_NEIGHBORS:
        i = 0
        while i < n - 2:
            if covered[i]:
                i += 1
                continue
            path_len = 1
            for j in range(i, n - 1):
                if covered[j + 1]:
                    break
                char = pwd_lower[j]
                next_char = pwd_lower[j + 1]
                if next_char != char and next_char in KEYBOARD_NEIGHBORS.get(char, set()):
                    path_len += 1
                else:
                    break
            if path_len >= 3:
                penalty += (path_len - 1) * char_entropy * 0.75
                for k in range(i, i + path_len):
                    covered[k] = True
                i += path_len
            else:
                i += 1

    return penalty


def detect_common_passwords(password: str) -> Tuple[float, bool, int]:
    pwd_lower = password.lower()

    if pwd_lower in COMMON_PASSWORDS:
        return 100.0, True, 1

    stripped = pwd_lower.strip(string.digits + string.punctuation + " ")
    if stripped and stripped in COMMON_PASSWORDS:
        return 60.0, True, 100

    for suffix_len in range(1, min(5, len(pwd_lower))):
        if pwd_lower[-suffix_len:].isdigit():
            base = pwd_lower[:-suffix_len]
            if base in COMMON_PASSWORDS:
                return 50.0, True, 100

    decoded = pwd_lower
    for leet, normal in LEET_REVERSE_MAP.items():
        decoded = decoded.replace(leet, normal)

    if decoded != pwd_lower:
        if decoded in COMMON_PASSWORDS or decoded.strip(string.digits + string.punctuation) in COMMON_PASSWORDS:
            return 45.0, True, 200

    return 0.0, False, 0


def detect_dictionary_words(password: str, char_entropy: float) -> Tuple[float, int, list]:
    if not DICT_WORDS_SET:
        return 0.0, 0, [False] * len(password)

    pwd_lower = password.lower()
    n = len(pwd_lower)
    covered = [False] * n
    matched_lengths = []

    for length in range(min(20, n), 3, -1):
        for start in range(n - length + 1):
            if any(covered[start:start + length]):
                continue
            substring = pwd_lower[start:start + length]
            if substring in DICT_WORDS_SET:
                matched_lengths.append(length)
                for k in range(start, start + length):
                    covered[k] = True

    word_count = len(matched_lengths)
    if word_count == 0:
        return 0.0, 0, covered

    penalty = 0.0
    for length in matched_lengths:
        raw_word_bits = length * char_entropy
        if word_count >= 3:
            true_word_bits = WORDLIST_ENTROPY_BITS
        elif word_count == 2:
            true_word_bits = 11.0
        else:
            true_word_bits = 8.0
        penalty += max(length * 1.5, raw_word_bits - true_word_bits)

    return penalty, word_count, covered


def detect_leet_speak(password: str, covered_by_dict: list) -> float:
    pwd_lower = password.lower()
    n = len(pwd_lower)
    leet_positions = [i for i, c in enumerate(pwd_lower) if c in LEET_REVERSE_MAP]

    if not leet_positions or not DICT_WORDS_SET:
        return 0.0

    decoded = "".join(LEET_REVERSE_MAP.get(c, c) for c in pwd_lower)
    if decoded == pwd_lower:
        return 0.0

    penalty = 0.0
    covered = list(covered_by_dict)

    for length in range(min(20, n), 3, -1):
        for start in range(n - length + 1):
            if any(covered[start:start + length]):
                continue
            sub_decoded = decoded[start:start + length]
            sub_orig = pwd_lower[start:start + length]
            if sub_decoded != sub_orig and sub_decoded in DICT_WORDS_SET:
                leet_in_word = sum(1 for c in sub_orig if c in LEET_REVERSE_MAP)
                penalty += length * 2.5 + leet_in_word * 3.0
                for k in range(start, start + length):
                    covered[k] = True

    return penalty


def analyze_password(password: str) -> Dict:
    if not password:
        return {
            "score": 0,
            "entropy_bits": 0.0,
            "effective_entropy": 0.0,
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
                "is_common": False,
                "common_position": 0
            }
        }

    analyzed_pwd = password[:256]
    length = len(password)

    charset_size, has_lower, has_upper, has_digit, has_symbol = calculate_charset_size(analyzed_pwd)
    char_entropy = math.log2(charset_size) if charset_size > 0 else 0.0
    entropy_bits = len(analyzed_pwd) * char_entropy

    repeat_penalty = detect_repeats(analyzed_pwd, char_entropy)
    sequence_penalty = detect_sequences(analyzed_pwd, char_entropy)
    keyboard_penalty = detect_keyboard_patterns(analyzed_pwd, char_entropy)
    common_penalty, is_common, common_position = detect_common_passwords(analyzed_pwd)
    dictionary_penalty, dict_word_count, covered_by_dict = detect_dictionary_words(analyzed_pwd, char_entropy)
    leet_penalty = detect_leet_speak(analyzed_pwd, covered_by_dict)

    total_penalty = (
        repeat_penalty + sequence_penalty + keyboard_penalty +
        common_penalty + dictionary_penalty + leet_penalty
    )

    effective_entropy = min(512.0, max(0.0, entropy_bits - total_penalty))
    if is_common and common_position == 1:
        effective_entropy = 0.0

    if is_common:
        score = 0
    elif effective_entropy < 28:
        score = 0
    elif effective_entropy < 36:
        score = 1
    elif effective_entropy < 60:
        score = 2
    elif effective_entropy < 90:
        score = 3
    else:
        score = 4

    warnings = []
    suggestions = []

    if repeat_penalty > char_entropy * 1.2:
        warnings.append("Содержит повторяющиеся символы или блоки")
    if sequence_penalty > 0:
        warnings.append("Содержит последовательности (1234, abcd)")
    if keyboard_penalty > 0:
        warnings.append("Содержит клавиатурный паттерн (qwerty, asdf)")
    if is_common:
        warnings.append("Является частым паролем или его вариацией")
    if dictionary_penalty > 0 and (dict_word_count < 3 or effective_entropy < 60):
        warnings.append("Содержит словарные слова")
    if leet_penalty > 0:
        warnings.append("Использует предсказуемые leet-speak замены (@ -> a, 0 -> o)")

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
    elif length < 16 and score < 4:
        suggestions.append("Для максимальной надёжности увеличьте длину до 16+ символов")

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
            "is_common": is_common,
            "common_position": common_position
        }
    }
