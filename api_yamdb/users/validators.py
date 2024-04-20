import re

from django.core.exceptions import ValidationError


def username_validator(username):
    valid_symbols = r"[\w.@+-]+"
    invalid_symbols = re.sub(valid_symbols, "", username)
    if invalid_symbols:
        raise ValidationError(
            f"Недопустимые символы в username: {invalid_symbols}"
        )
    if username == "me":
        raise ValidationError(
            "Недопустимое значение username: me"
        )
