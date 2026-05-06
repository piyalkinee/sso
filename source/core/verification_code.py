import random
from datetime import datetime, timedelta

from loguru import logger

from ..configuration import conf


def generate_verification_code() -> str:
    code_length = conf['verification']['code_length']
    return ''.join([str(random.randint(0, 9)) for _ in range(code_length)])


def get_code_expiration_time() -> datetime:
    return datetime.utcnow() + timedelta(seconds=conf['verification']['code_ttl'])


def format_phone_number(phone: str) -> str:
    digits = ''.join(filter(str.isdigit, phone))
    if digits.startswith('8') and len(digits) == 11:
        digits = '7' + digits[1:]
    return '+' + digits
