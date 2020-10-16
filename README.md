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
import os

INSTALLED_APPS = [
    # ...
    'django_user_email_extension',
    # ...
]

###############################
# Define the default user model 
###############################
AUTH_USER_MODEL = 'django_user_email_extension.User'

# if set then users age will be validated for minimal age (in years)
USER_MINIMAL_AGE = int(os.environ.get('USER_MINIMAL_AGE', None))

# if set, used address cannot be saved with non verified phone number
ENFORCE_USER_ADDRESS_VERIFIED_PHONE = int(os.environ.get('ENFORCE_USER_ADDRESS_VERIFIED_PHONE', False)) 

EMAIL_USE_TLS = True
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('email_host')
EMAIL_PORT = os.environ.get('email_port')
EMAIL_HOST_USER = os.environ.get('email_username')
EMAIL_HOST_PASSWORD = os.environ.get('email_password')

# optional, if not set, verification email will never expire.
DJANGO_EMAIL_VERIFIER_EXPIRE_TIME = 24  # In Hours
```

Run migrations:
```shell script
python3 manage.py makemigrations
python3 manage.py migrate
```

Usage Example
-------------
use:

```python
from django.contrib.auth import get_user_model

User = get_user_model()

user_object = User.objects.create_user(
    email='EMAIL',
    password='PASSWORD'
)

# .save() must be called
# this option has been modified so extra action could be executed before final user creation
user_object.save()

# user is a Django User object
user_object.create_verification_email()

# Send the verification email
user_object.send_verification_email(
    subject=subject,
    body=body,  # *** view body example below to contain the unique UUID
    from_mail=EMAIL_HOST_USER
)
```
Then when user click the link (from the body sent via email)
```python
# make sure url is getting a uuid key in urls.py
path('verify_account/<uuid:verification_uuid>/', views.VerifyEmailUUIDView.as_view(), name='verify_account')

# initiate verification process on the return view
ver_uuid = DjangoEmailVerifier.objects.get(verification_uuid='UUID_FROM_REQUEST')
ver_uuid.verify_record()
```

The confirmation uuid can be sent as part of the body for example:
```python
body = 'Follow this link to verify your account: https://nalkins.cloud{}'.format(
    reverse('verify_account', kwargs={'verification_uuid': str(user_object.get_uuid_of_email())})
)
```
