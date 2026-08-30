KEYBOARD_NEIGHBORS = {
    'q': {'w', 'a', '1', '2'},
    'w': {'q', 'e', 'a', 's', '2', '3'},
    'e': {'w', 'r', 's', 'd', '3', '4'},
    'r': {'e', 't', 'd', 'f', '4', '5'},
    't': {'r', 'y', 'f', 'g', '5', '6'},
    'y': {'t', 'u', 'g', 'h', '6', '7'},
    'u': {'y', 'i', 'h', 'j', '7', '8'},
    'i': {'u', 'o', 'j', 'k', '8', '9'},
    'o': {'i', 'p', 'k', 'l', '9', '0'},
    'p': {'o', '[', 'l', ';', '0', '-'},
    'a': {'q', 'w', 's', 'z', '1'},
    's': {'a', 'w', 'e', 'd', 'z', 'x'},
    'd': {'s', 'e', 'r', 'f', 'x', 'c'},
    'f': {'d', 'r', 't', 'g', 'c', 'v'},
    'g': {'f', 't', 'y', 'h', 'v', 'b'},
    'h': {'g', 'y', 'u', 'j', 'b', 'n'},
    'j': {'h', 'u', 'i', 'k', 'n', 'm'},
    'k': {'j', 'i', 'o', 'l', 'm', ','},
    'l': {'k', 'o', 'p', ';', ',', '.'},
    'z': {'a', 's', 'x'},
    'x': {'z', 's', 'd', 'c'},
    'c': {'x', 'd', 'f', 'v'},
    'v': {'c', 'f', 'g', 'b'},
    'b': {'v', 'g', 'h', 'n'},
    'n': {'b', 'h', 'j', 'm'},
    'm': {'n', 'j', 'k', ','},
    '1': {'2', 'q'},
    '2': {'1', '3', 'q', 'w'},
    '3': {'2', '4', 'w', 'e'},
    '4': {'3', '5', 'e', 'r'},
    '5': {'4', '6', 'r', 't'},
    '6': {'5', '7', 't', 'y'},
    '7': {'6', '8', 'y', 'u'},
    '8': {'7', '9', 'u', 'i'},
    '9': {'8', '0', 'i', 'o'},
    '0': {'9', '-', 'o', 'p'},
    '-': {'0', '=', 'p', '['},
    '=': {'-', '['},
    '[': {'-', ']', 'p', ';'},
    ']': {'[', '\\', ';', '\''},
    '\\': {']', '\''},
    ';': {'l', '[', ']', '\''},
    '\'': {';', ']'},
    ',': {'m', 'k', 'l', '.'},
    '.': {',', 'l', ';', '/'},
    '/': {'.', ';'}
}

COMMON_KEYBOARD_WALKS = [
    "qwerty", "qwertyu", "qwertyui", "qwertyuio", "qwertyuiop",
    "asdf", "asdfg", "asdfgh", "asdfghj", "asdfghjk", "asdfghjkl",
    "zxcv", "zxcvb", "zxcvbn", "zxcvbnm",

    "ytrewq", "uytrewq", "iuytrewq", "oiuytrewq", "poiuytrewq",
    "fdsa", "gfdsa", "hgfdsa", "jhgfdsa", "kjhgfdsa", "lkjhgfdsa",
    "vcxz", "bvcxz", "nbvcxz", "mnbvcxz",

    "qaz", "wsx", "edc", "rfv", "tgb", "yhn", "ujm",
    "zaq", "xsw", "cde", "vfr", "bgt", "nhy", "mju",

    "qweasd", "qweasdzx", "qazwsx", "qazwsxedc",

    "1234", "12345", "123456", "1234567", "12345678", "123456789", "1234567890",
    "0987", "09876", "098765", "0987654", "09876543", "098765432", "0987654321",

    "qweasdzxc", "qazwsxedcrfv", "plmokn", "plmokn2",

    "qweqwe", "asdfasdf", "zxcvzxcv",

    "1qaz", "2wsx", "3edc", "4rfv", "5tgb", "6yhn", "7ujm",
    "1qaz2wsx", "1qaz2wsx3edc",

    "qwertz", "qwertzu", "qwertzui",

    "azerty", "azertyu", "azertyui"
]