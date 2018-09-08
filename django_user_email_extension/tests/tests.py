
import datetime
from django.test import TestCase
from django_user_email_extension.models import *


class TestUserModel(TestCase):

    def setUp(self):
        self.user = User(email="test@nalkins.cloud",
                         user_name="arie",
                         first_name="arie",
                         last_name="lev",
                         address="",
                         city="",
                         country="",
                         postal_code=12345,
                         phone_number="12345678",
                         linkedin="")

    def test_is_user(self):
        self.assertEqual(self.user.USERNAME_FIELD, "email")

    def test_get_full_name(self):
        self.assertEqual(self.user.get_full_name(), "arie lev")

    def test_get_first_name(self):
        self.assertEqual(self.user.get_first_name(), "arie")

    def test_get_last_name(self):
        self.assertEqual(self.user.get_last_name(), "lev")

    def test_create_verification_email(self):
        self.user.create_verification_email()
        email_ver_object = DjangoEmailVerifier.objects.get(email=self.user.email)

        self.assertEqual(email_ver_object.email, "test@nalkins.cloud")


class TestDjangoEmailVerifierModel(TestCase):

    def setUp(self):
        self.user = User(email="test@nalkins.cloud")
        self.email_object = DjangoEmailVerifier.objects.create(user=self.user,
                                                               email=self.user.email)

    def test_is_email_verification(self):
        self.assertEqual(self.email_object.REQUIRED_FIELDS, ['user'])

    def test_verified(self):
        self.assertFalse(self.email_object.verified())

    def test_uuid_expire_date(self):
        expected_expire = datetime.datetime.now().replace(microsecond=0, second=0, minute=0) + timedelta(hours=25)
        actual_expire = self.email_object.uuid_expire_date().replace(microsecond=0, second=0, minute=0, tzinfo=None)
        self.assertEqual(expected_expire, actual_expire)

    def test_is_uuid_expired(self):
        self.assertFalse(self.email_object.is_uuid_expired())

# TODO Add managers tests
# class TestUserManager(TestCase):
#
#     def test_create_user(self):
#         User.objects.create()
#
#
# class TestDjangoEmailVerifierManger(TestCase):
#
#     def setUp(self):
#         self.user = User(email="test@nalkins.cloud")
#
#     def test_create_verification(self):
#         DjangoEmailVerifier.objects.create_verification(email=self.user.email, user=self.user)
#
#     # def test_get_uuid_of_email(self):
#     #     uuid_num = self.user.get_uuid_of_email()
#     #     self.assertEqual(uuid_num, "(?P<uuid>[a-z0-9\-]+)")
