import secrets
import string
from typing import List, Optional
try:
    from app.data.wordlist_eff import WORDLIST
except ImportError:
    WORDLIST = [
        "abacus", "abdomen", "abdominal", "abide", "ability", "ablaze", "able", "abnormal", "abort", "about",
        "above", "abrasion", "absorb", "abstract", "absurd", "abuse", "academy", "accent", "accept", "access",
        "accident", "acclaim", "account", "accuracy", "accurate", "achieve", "acid", "acoustic", "acquire", "across",
        "action", "activate", "actor", "actress", "actual", "adapt", "addition", "address", "adequate", "adjust",
        "admin", "admire", "admit", "adopt", "adult", "advance", "adventure", "advice", "aerial", "affair",
        "affect", "afford", "afraid", "after", "again", "agency", "agenda", "agent", "aggressive", "agree",
        "ahead", "aim", "air", "airport", "aisle", "alarm", "album", "alcohol", "alert", "alien",
        "alive", "alley", "allow", "almost", "alone", "alpha", "already", "also", "alter", "always",
        "amateur", "amazing", "among", "amount", "amused", "analyst", "anchor", "ancient", "anger", "angle",
        "angry", "animal", "ankle", "announce", "annual", "another", "answer", "antenna", "antique", "anxiety",
        "any", "apart", "apology", "appear", "apple", "approve", "april", "arch", "arctic", "area",
        "arena", "argue", "arm", "armed", "armor", "army", "around", "arrange", "arrest", "arrive",
        "arrow", "art", "artefact", "artist", "artwork", "ask", "aspect", "assault", "asset", "assist",
        "assume", "asthma", "athlete", "atom", "attack", "attend", "attitude", "attract", "auction", "audit",
        "august", "aunt", "author", "auto", "autumn", "average", "avocado", "avoid", "awake", "aware",
        "awesome", "awful", "awkward", "axis", "baby", "bachelor", "bacon", "badge", "bag", "balance",
        "balcony", "ball", "bamboo", "banana", "banner", "bar", "barely", "bargain", "barrel", "base",
        "basic", "basket", "battle", "beach", "bean", "beauty", "because", "become", "beef", "before",
        "begin", "behave", "behind", "believe", "below", "belt", "bench", "benefit", "best", "betray",
        "better", "between", "beyond", "bicycle", "bid", "bike", "bind", "biology", "bird", "birth",
        "bitter", "black", "blade", "blame", "blanket", "blast", "bleak", "bless", "blind", "blood"
    ]


def generate_classic(
        length: int = 16,
        use_upper: bool = True,
        use_lower: bool = True,
        use_digits: bool = True,
        use_symbols: bool = True,
        exclude_chars: str = "",
        min_of_each: bool = True
) -> str:
    alphabet = ""
    required_chars = []

    if use_lower:
        lower = string.ascii_lowercase
        alphabet += lower
        required_chars.append(secrets.choice(lower))
    if use_upper:
        upper = string.ascii_uppercase
        alphabet += upper
        required_chars.append(secrets.choice(upper))
    if use_digits:
        digits = string.digits
        alphabet += digits
        required_chars.append(secrets.choice(digits))
    if use_symbols:
        symbols = "!@#$%^&*()-_=+[]{}|;:',.<>?/~"
        alphabet += symbols
        required_chars.append(secrets.choice(symbols))

    if not alphabet:
        raise ValueError("Должен быть выбран хотя бы один набор символов")

    if exclude_chars:
        alphabet = "".join(c for c in alphabet if c not in exclude_chars)
        required_chars = [c for c in required_chars if c not in exclude_chars]

    if not alphabet:
        raise ValueError("После исключения символов алфавит пуст")

    if min_of_each and required_chars:
        remaining_length = max(0, length - len(required_chars))
        password_chars = required_chars + [secrets.choice(alphabet) for _ in range(remaining_length)]
        secrets.SystemRandom().shuffle(password_chars)
    else:
        password_chars = [secrets.choice(alphabet) for _ in range(length)]

    return "".join(password_chars)


def generate_passphrase(
        word_count: int = 5,
        separator: str = "-",
        capitalize: bool = True,
        add_number: bool = True,
        add_symbol: bool = True
) -> str:
    words = [secrets.choice(WORDLIST) for _ in range(word_count)]

    if capitalize:
        words = [w.capitalize() for w in words]

    parts = list(words)

    if add_number:
        num = str(secrets.randbelow(999) + 1)
        pos = secrets.randbelow(len(parts) + 1)
        parts.insert(pos, num)

    if add_symbol:
        sym = secrets.choice("!@#$%^&*")
        pos = secrets.randbelow(len(parts) + 1)
        parts.insert(pos, sym)

    return separator.join(parts)


def generate_pronounceable(length: int = 12) -> str:
    vowels = ['a', 'e', 'i', 'o', 'u', 'ai', 'ea', 'ou', 'oo', 'ee']
    consonants = [
        'b', 'c', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'm', 'n', 'p', 'r', 's', 't', 'v', 'w', 'z',
        'bl', 'br', 'cl', 'cr', 'dr', 'fl', 'fr', 'gl', 'gr', 'pl', 'pr', 'sc', 'sk', 'sl', 'sm',
        'sn', 'sp', 'st', 'str', 'sw', 'tr', 'tw'
    ]

    password = ""
    start_with_vowel = secrets.choice([True, False])

    while len(password) < length:
        if start_with_vowel:
            password += secrets.choice(vowels)
        else:
            password += secrets.choice(consonants)
        start_with_vowel = not start_with_vowel

    password = password[:length]

    replacements = secrets.randbelow(2) + 1
    indices = secrets.SystemRandom().sample(range(len(password)), min(replacements, len(password)))
    for i in indices:
        if secrets.choice([True, False]):
            password = password[:i] + str(secrets.randbelow(10)) + password[i + 1:]
        else:
            password = password[:i] + secrets.choice("!@#$%") + password[i + 1:]
    password = password[0].upper() + password[1:]

    return password


def generate_pattern(pattern_template: str) -> str:
    result = []
    for char in pattern_template:
        if char == 'W':
            result.append(secrets.choice(WORDLIST))
        elif char == 'D':
            result.append(str(secrets.randbelow(10)))
        elif char == 'S':
            result.append(secrets.choice("!@#$%^&*"))
        elif char == 'L':
            result.append(secrets.choice(string.ascii_lowercase))
        elif char == 'U':
            result.append(secrets.choice(string.ascii_uppercase))
        else:
            result.append(char)
    return "".join(result)


def generate_password(method: str, **kwargs) -> str:
    if method == "classic":
        return generate_classic(**kwargs)
    elif method == "passphrase":
        return generate_passphrase(**kwargs)
    elif method == "pronounceable":
        return generate_pronounceable(**kwargs)
    elif method == "pattern":
        return generate_pattern(**kwargs)
    else:
        raise ValueError(f"Неизвестный метод генерации: {method}")