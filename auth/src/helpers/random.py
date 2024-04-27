import string
from secrets import choice


def get_random_string(length: int):
    alphabet = string.ascii_letters + string.digits
    return "".join(choice(alphabet) for _ in range(length))
