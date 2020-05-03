from datetime import timedelta

from django.db.utils import IntegrityError
from django.test import TestCase

from django_user_email_extension.models import User, DjangoEmailVerifier, Address, PhoneNumber


class TestUserModel(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(email="test@nalkins.cloud",
                                             user_name="arie",
                                             first_name="arie",
                                             last_name="lev",
                                             gender="m",
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


class TestAddressModel(TestCase):
    def setUp(self):
        self.address_1 = Address.objects.create(street_name="98 Columbus Ave",
                                                street_number="Floor 5, Apartment 15",
                                                city="San Francisco",
                                                state="California",
                                                country='US',
                                                zip_code=123456)
        # apartment 24
        self.address_2 = Address.objects.create(street_name='441 Broadway St',
                                                street_number='Apartment 24',
                                                city='New York',
                                                state="NY",
                                                country='USA',
                                                zip_code=000000)
        # apartment 13
        self.address_3 = Address.objects.create(street_name='441 Broadway St',
                                                street_number='Apartment 13',
                                                city='New York',
                                                state="NY",
                                                country='USA',
                                                zip_code=000000,
                                                timezone='US/Eastern')

    def test_address_model(self):
        # should be 2 addresses with street '441 Broadway St'
        self.assertEqual(len(Address.objects.filter(street_name='441 Broadway St')), 2)

        # test string prints
        self.assertEqual(str(self.address_1),
                         '98 Columbus Ave Floor 5, Apartment 15 San Francisco, California, 123456, US')

    def test_unique_address(self):
        # This is should be single here due to this bug https://code.djangoproject.com/ticket/21540

        # test unique constraint ('street_name', 'street_number', 'city', 'state', 'country')
        with self.assertRaises(IntegrityError):
            Address.objects.create(street_name='441 Broadway St',
                                   street_number='Apartment 13',
                                   city='New York',
                                   state="NY",
                                   country='USA',
                                   zip_code=000000,
                                   timezone='US/Eastern')

    def test_country_field(self):
        # test country field https://github.com/SmileyChris/django-countries#countryfield

        country_field_object = Address.objects.filter(street_name='441 Broadway St',
                                                      street_number='Apartment 24').first().country
        self.assertEqual(country_field_object.name, 'United States of America')
        self.assertEqual(country_field_object.code, 'US')
        self.assertEqual(country_field_object.alpha3, 'USA')


class TestUserAddressInteraction(TestCase):
    def setUp(self):
        self.address_1 = Address.objects.create(street_name="98 Columbus Ave",
                                                street_number="Floor 5, Apartment 15",
                                                city="San Francisco",
                                                state="California",
                                                country='US',
                                                zip_code=123456)
        self.address_2 = Address.objects.create(street_name='441 Broadway St',
                                                street_number='Apartment 24',
                                                city='New York',
                                                state="NY",
                                                country='USA',
                                                zip_code=000000)
        self.user = User.objects.create_user(email="test_address@nalkins.cloud")
        self.user.address.add(self.address_1, self.address_2)

    def test_user_addresses(self):
        # current user should have 2 addresses
        self.assertEqual(len(self.user.address.all()), 2)


class TestPhoneNumberModel(TestCase):
    def setUp(self):
        self.number_1 = PhoneNumber.objects.create(number='+1-212-509-5555',
                                                   type='m',
                                                   verified=False)

        self.number_1.full_clean()
        self.number_2 = PhoneNumber.objects.create(number='+972-50-123-4567',
                                                   type='m',
                                                   verified=False)
        self.number_2.full_clean()

    def test_model(self):

        # test get_mobile_number_carrier
        self.assertEqual('', self.number_1.get_mobile_number_carrier())
        self.assertEqual('Pelephone', self.number_2.get_mobile_number_carrier())

        # test get_number_location_description
        self.assertEqual('New York, NY', self.number_1.get_number_location_description())
