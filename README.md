Django-User-Email-Extension
===========================
[![](https://img.shields.io/pypi/v/django-user-email-extension.svg)](https://pypi.org/project/django-user-email-extension/)
[![](https://img.shields.io/pypi/l/django-user-email-extension.svg?colorB=blue)](https://pypi.org/project/django-user-email-extension/)
[![](https://img.shields.io/pypi/pyversions/django-user-email-extension.svg)](https://pypi.org/project/django-user-email-extension/)
[![](https://img.shields.io/pypi/djversions/django-user-email-extension.svg)](https://pypi.org/project/django-user-email-extension/)

Django application that extends User module, and provides email verification process.

Install
-------
`pip install django-user-email-extension`

Add to installed apps, and email provider details:

```python
INSTALLED_APPS = [
    # ...
    'django_user_email_extension',
    # ...
]
# if set then users age will be validated for minimal age (in years)
USER_MINIMAL_AGE = int(os.environ.get('USER_MINIMAL_AGE', None))

# if set, an used address canot be save with non verified phone number
ENFORCE_USER_ADDRESS_VERIFIED_PHONE = int(os.environ.get('ENFORCE_USER_ADDRESS_VERIFIED_PHONE', False)) 

EMAIL_USE_TLS = True
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('email_host')
EMAIL_PORT = os.environ.get('email_port')
EMAIL_HOST_USER = os.environ.get('email_username')
EMAIL_HOST_PASSWORD = os.environ.get('email_password')
```

Run migrations:

`python3 manage.py makemigrations`
`python3 manage.py migrate`

Optional:

add to settings.py, if not set, verification email will never expire.

```python
    # ...
    DJANGO_EMAIL_VERIFIER_EXPIRE_TIME = 24  # In Hours
    # ...
```


Usage Example
-------------
use:

```python
from django_user_email_extension.models import *

user_object = User.objects.create_user('EMAIL', 'PASSWORD')

# user is a Django User object
user_object.create_verification_email()

# Send the verification email
user_object.send_verification_email(subject=subject,
                                 body=body,
                                 from_mail=EMAIL_HOST_USER)

# Initiate verification process
verify_record(uuid_value=uuid)
```

The confirmation uuid can be sent as part of the body for example:

```python
    body = 'Follow this link to verify your account: https://nalkins.cloud' + \
           '%s' % reverse('verify_account',
                          kwargs={'uuid': str(user_object.get_uuid_of_email())})
```