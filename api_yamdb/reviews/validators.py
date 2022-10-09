import datetime as dt
import re

from django.core.exceptions import ValidationError


def validate_username(value):
    if value == 'me':
        raise ValidationError(
            ('Запрещено использовать логин me'),
            params={'value': value},
        )
    reg = re.compile(r'^[\w.@+-]+$')
    if not bool(re.fullmatch(reg, value)):
        raise ValidationError('Недопустимый символ в username.')


def validate_year(value):
    year = dt.date.today().year
    if (value > year):
        raise ValidationError(
            'Нельзя добавлять произведения будущего!'
        )
