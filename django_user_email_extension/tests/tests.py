from datetime import timedelta

from django.test import TestCase

from django_user_email_extension.models import User, DjangoEmailVerifier, Location


class TestUserModel(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(email="test@nalkins.cloud",
                                             user_name="arie",
                                             first_name="arie",
                                             last_name="lev",
                                             gender="m",
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
        self.user = User.objects.create(email="test@nalkins.cloud")
        self.email_object = DjangoEmailVerifier.objects.create(user=self.user,
                                                               email=self.user.email)

    def test_to_string(self):
        """
        Test DjangoEmailVerifier __str__ function
        :return:
        """
        self.assertEqual(str(self.email_object), 'Email Verification for User: ' + self.user.email)

    def test_is_email_verification(self):
        """
        Test that required fields is 'user'
        :return:
        """
        self.assertEqual(self.email_object.REQUIRED_FIELDS, ['user'])

    def test_verified(self):
        """
        Test verified() function
        :return:
        """
        self.assertFalse(self.email_object.verified())
        self.email_object.is_verified = True
        self.assertTrue(self.email_object.verified())

    def test_uuid_expire_date(self):
        """
        Test email verification expiration,
        since test.setting.DJANGO_EMAIL_VERIFIER_EXPIRE_TIME value is 25, adding timedelta of 25 hours
        :return:
        """
        expected_expire = self.email_object.date_created.replace(microsecond=0,
                                                                 second=0,
                                                                 minute=0) + timedelta(hours=25)
        actual_expire = self.email_object.uuid_expire_date().replace(microsecond=0,
                                                                     second=0,
                                                                     minute=0)
        self.assertEqual(expected_expire, actual_expire)

    def test_is_uuid_expired(self):
        self.assertFalse(self.email_object.is_uuid_expired())


class TestUserManager(TestCase):

    def setUp(self):
        self.user = User.objects.create(email="test_user_manager@nalkins.cloud")
        DjangoEmailVerifier.objects.create_verification(email=self.user.email,
                                                        user=self.user)

    def test_create_user(self):
        User.objects.create(email="test_create_user@nalkins.cloud")

    def test_get_uuid_of_email(self):
        email_object = DjangoEmailVerifier.objects.get(email=self.user.email)
        uuid_num = self.user.email_verification_obj.get_uuid_of_email(email_object.email)
        self.assertRegex(str(uuid_num), '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}')


class TestDjangoEmailVerifierManger(TestCase):

    def setUp(self):
        self.user = User.objects.create(email="test_verification_manager@nalkins.cloud")
        DjangoEmailVerifier.objects.create_verification(email=self.user.email, user=self.user)

    def test_create_verification(self):
        self.assertEqual(DjangoEmailVerifier.objects.get(email=self.user.email).email,
                         "test_verification_manager@nalkins.cloud")

    def test_get_uuid_of_email(self):
        self.email_object = DjangoEmailVerifier.objects.get(email=self.user.email)
        uuid_num = DjangoEmailVerifier.objects.get_uuid_of_email(self.email_object.email)
        self.assertRegex(str(uuid_num), '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}')


class TestLocationModel(TestCase):
    def setUp(self):
        self.location_1 = Location.objects.create_location(address="some street 40, apartment 10",
                                                           city="California",
                                                           state="CA",
                                                           country='US',
                                                           postal_code=123456)
        self.location_2 = Location.objects.create_location(address="wall street 5, apartment 10",
                                                           city="New York",
                                                           state="NY",
                                                           country='US',
                                                           postal_code=000000)
        self.user = User.objects.create_user(email="test_location@nalkins.cloud")
        self.user.address.add(self.location_1, self.location_2)

    def test_location_values(self):
        # current user should have 2 addresses
        self.assertEqual(len(self.user.address.all()), 2)

        country_name = self.user.address.get(address="wall street 5, apartment 10",
                                             city='New York',
                                             state="NY",
                                             country='US').country.name
        self.assertEqual(country_name, 'United States of America')
