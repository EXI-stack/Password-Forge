import logging
import secrets
import string

logger = logging.getLogger(__name__)

try:
    from app.data.wordlist_eff import WORDLIST
except ImportError:
    logger.warning("Не удалось загрузить полный словарь app.data.wordlist_eff. Используется резервный словарь.")
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

SYMBOLS_CHARSET = "!@#$%^&*()-_=+[]{}|;:',.<>?/~"
SHORT_SYMBOLS_CHARSET = "!@#$%^&*"


def generate_classic(
        length: int = 16,
        use_upper: bool = True,
        use_lower: bool = True,
        use_digits: bool = True,
        use_symbols: bool = True,
        exclude_chars: str = "",
        min_of_each: bool = True
) -> str:
    length = int(length)
    if length < 4 or length > 256:
        raise ValueError("Длина пароля должна быть от 4 до 256 символов")

    if not any([use_lower, use_upper, use_digits, use_symbols]):
        raise ValueError("Должен быть выбран хотя бы один набор символов")

    exclude_set = set(exclude_chars) if exclude_chars else set()
    pools = []

    if use_lower:
        lower = "".join(c for c in string.ascii_lowercase if c not in exclude_set)
        if not lower and min_of_each:
            raise ValueError("Все строчные буквы были исключены")
        if lower:
            pools.append(lower)

    if use_upper:
        upper = "".join(c for c in string.ascii_uppercase if c not in exclude_set)
        if not upper and min_of_each:
            raise ValueError("Все заглавные буквы были исключены")
        if upper:
            pools.append(upper)

    if use_digits:
        digits = "".join(c for c in string.digits if c not in exclude_set)
        if not digits and min_of_each:
            raise ValueError("Все цифры были исключены")
        if digits:
            pools.append(digits)

    if use_symbols:
        symbols = "".join(c for c in SYMBOLS_CHARSET if c not in exclude_set)
        if not symbols and min_of_each:
            raise ValueError("Все спецсимволы были исключены")
        if symbols:
            pools.append(symbols)

    alphabet = "".join(pools)
    if not alphabet:
        raise ValueError("После исключения символов алфавит пуст")

    if min_of_each and pools:
        if length < len(pools):
            raise ValueError(f"Длина пароля ({length}) меньше числа выбранных наборов ({len(pools)})")
        required_chars = [secrets.choice(pool) for pool in pools]
        remaining_length = length - len(required_chars)
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
    word_count = int(word_count)
    if word_count < 3 or word_count > 16:
        raise ValueError("Количество слов должно быть от 3 до 16")
    if len(separator) > 3:
        raise ValueError("Разделитель не должен превышать 3 символов")
    if not WORDLIST:
        raise ValueError("Словарь для генерации фраз пуст")

    words = [secrets.choice(WORDLIST) for _ in range(word_count)]

    if capitalize:
        words = [w.capitalize() for w in words]

    if add_number:
        num = str(secrets.randbelow(1000))
        pos = secrets.randbelow(len(words))
        words[pos] = f"{words[pos]}{num}"

    if add_symbol:
        sym = secrets.choice(SHORT_SYMBOLS_CHARSET)
        pos = secrets.randbelow(len(words))
        words[pos] = f"{words[pos]}{sym}"

    return separator.join(words)


def generate_pronounceable(length: int = 12) -> str:
    length = int(length)
    if length < 6 or length > 64:
        raise ValueError("Длина произносимого пароля должна быть от 6 до 64 символов")

    vowels = ['a', 'e', 'i', 'o', 'u', 'ai', 'ea', 'ou', 'oo', 'ee']
    consonants = [
        'b', 'c', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'm', 'n', 'p', 'r', 's', 't', 'v', 'w', 'z',
        'bl', 'br', 'cl', 'cr', 'dr', 'fl', 'fr', 'gl', 'gr', 'pl', 'pr', 'sc', 'sk', 'sl', 'sm',
        'sn', 'sp', 'st', 'str', 'sw', 'tr', 'tw'
    ]

    password = ""
    use_vowel = secrets.choice([True, False])

    while len(password) < length:
        if use_vowel:
            password += secrets.choice(vowels)
        else:
            password += secrets.choice(consonants)
        use_vowel = not use_vowel

    chars = list(password[:length])
    chars[0] = chars[0].upper()
    indices = secrets.SystemRandom().sample(range(1, length), 2)
    chars[indices[0]] = str(secrets.randbelow(10))
    chars[indices[1]] = secrets.choice(SHORT_SYMBOLS_CHARSET)

    return "".join(chars)


def generate_pattern(pattern_template: str) -> str:
    if not pattern_template or not pattern_template.strip():
        raise ValueError("Шаблон не может быть пустым")
    if len(pattern_template) > 128:
        raise ValueError("Шаблон слишком длинный (максимум 128 символов)")
    if not WORDLIST:
        raise ValueError("Словарь для шаблона пуст")

    result = []
    i = 0
    n = len(pattern_template)

    while i < n:
        char = pattern_template[i]
        if char == '\\' and i + 1 < n:
            result.append(pattern_template[i + 1])
            i += 2
            continue

        if char == 'W':
            result.append(secrets.choice(WORDLIST).capitalize())
        elif char == 'w':
            result.append(secrets.choice(WORDLIST).lower())
        elif char == 'D':
            result.append(str(secrets.randbelow(10)))
        elif char == 'S':
            result.append(secrets.choice(SHORT_SYMBOLS_CHARSET))
        elif char == 'L':
            result.append(secrets.choice(string.ascii_lowercase))
        elif char == 'U':
            result.append(secrets.choice(string.ascii_uppercase))
        else:
            result.append(char)
        i += 1

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
