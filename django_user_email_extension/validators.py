
from django.core.validators import RegexValidator


def phone_number_validator():
    return RegexValidator(regex=r'^\+?1?\d{12,15}$',
                          message="Phone number must be entered in the format of: '+18501234567'. "
                                  "Minimum 12 digits and up to 15 digits allowed.")
