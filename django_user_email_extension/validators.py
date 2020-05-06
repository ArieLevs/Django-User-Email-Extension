
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.conf import settings
from datetime import datetime


def phone_number_validator():
    return RegexValidator(regex=r'^\+?1?\d{12,15}$',
                          message="Phone number must be entered in the format of: '+18501234567'. "
                                  "Minimum 12 digits and up to 15 digits allowed.")


def validate_users_min_age(birth_date):
    if hasattr(settings, 'USER_MINIMAL_AGE'):
        minimal_age = int(settings.USER_MINIMAL_AGE)
        if minimal_age:
            from_date = datetime.now().date()
            try:
                x_years_ago = from_date.replace(year=from_date.year - minimal_age)
            except ValueError:  # 29th of february and not a leap year
                x_years_ago = from_date.replace(month=2, day=28, year=from_date.year - minimal_age)

            # in case birth date i bigger, then the date x years ago
            if birth_date > x_years_ago:
                raise ValidationError(message='Age must be at least {} years old.'.format(minimal_age))


def validate_alphabetic_string(string):
    """
    just use https://docs.python.org/3/library/stdtypes.html#str.isalpha
    :param string: string to validate
    :return: boolean id string is alphabetic
    """
    if not string.isalpha():
        raise ValidationError(message='Must be Alphabet string.')
