
from django.test import TestCase
from django_user_email_extension.models import *


class TestUserModel(TestCase):

    def setUp(self):
        self.user = User(email="test@nalkins.cloud")

    def test_is_user(self):
        with self.assertRaises(AttributeError):
            self.user.first_name
        with self.assertRaises(AttributeError):
            self.user.last_name
        self.assertEqual(self.user.USERNAME_FIELD, "email")
