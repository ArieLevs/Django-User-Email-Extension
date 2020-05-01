
import sys
import os
import django
from django.conf import settings
from django.core.management import call_command


def run_tests():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_user_email_extension.tests.settings')
    django.setup()

    if not settings.configured:
        print("No setting configurations found, exiting")
        exit(1)

    test_output = call_command('test', 'django_user_email_extension', interactive=True, failfast=False, verbosity=2)

    sys.exit(bool(test_output))


if __name__ == "__main__":
    run_tests()
