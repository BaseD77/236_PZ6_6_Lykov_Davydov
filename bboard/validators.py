from django.core.exceptions import ValidationError
import re

# Функции-валидаторы Django может сериализовать
def validate_price_not_zero(value):
    if value <= 0:
        raise ValidationError(
            'Цена должна быть больше нуля',
            code='invalid_price'
        )

def validate_phone_number(value):
    pattern = r'^\+?1?\d{9,15}$'
    if not re.match(pattern, value):
        raise ValidationError(
            'Некорректный формат телефона',
            code='invalid_phone'
        )

def validate_no_bad_words(value):
    bad_words = ['спам', 'мошенничество', 'обман']
    for word in bad_words:
        if word in value.lower():
            raise ValidationError(
                f'Заголовок содержит запрещенное слово: "{word}"',
                code='bad_word'
            )

# Валидаторы-классы нужно обернуть в функции для сериализации
def validate_price_range(value):
    min_price = 1
    max_price = 10000000
    if value < min_price:
        raise ValidationError(
            f'Цена не может быть меньше {min_price}',
            code='price_too_low'
        )
    if value > max_price:
        raise ValidationError(
            f'Цена не может превышать {max_price}',
            code='price_too_high'
        )

def validate_text_length_min_5_max_50(value):
    if len(value) < 5:
        raise ValidationError(
            'Текст должен содержать не менее 5 символов',
            code='text_too_short'
        )
    if len(value) > 50:
        raise ValidationError(
            'Текст не должен превышать 50 символов',
            code='text_too_long'
        )

def validate_text_length_min_20_max_5000(value):
    if len(value) < 20:
        raise ValidationError(
            'Текст должен содержать не менее 20 символов',
            code='text_too_short'
        )
    if len(value) > 5000:
        raise ValidationError(
            'Текст не должен превышать 5000 символов',
            code='text_too_long'
        )