import re
import uuid
from datetime import timedelta, datetime, timezone

import pytz
from django.conf import settings
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.validators import MinLengthValidator
from django.core.validators import validate_email
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField

from django_user_email_extension.languages import LANGUAGES
from django_user_email_extension.validators import validate_users_min_age, validate_alphabetic_string
from . import ZIP_CODES_REGEX


class PhoneNumberManager(models.Manager):

    def get_all_phone_numbers_of_user(self, user):
        """
        return all phone numbers associated of user
        :param user: User object
        :return: QuerySet of PhoneNumber object, or empty
        """
        return self.all().filter(owner=user)

    def get_verified_phone_numbers_of_user(self, user):
        """
        return only verified phone numbers of user
        :param user: User object
        :return: QuerySet of PhoneNumber object(s), or empty
        """
        return self.all().filter(owner=user, verified=True)

    def get_verified_number_list(self, user):
        """
        return a list of verified numbers.

        return example [<PhoneNumber: +41524204242>, <PhoneNumber: +972535251234>]
        :param user: User object
        :return: list of PhoneNumberField
        """
        result = []
        for phone_object in self.get_verified_phone_numbers_of_user(user=user):
            result.append(phone_object.number)
        return result

    def get_default_number_of_user(self, user):
        """
        return users default number,
        there can be 0 or max 1 defaults
        :param user: User object
        :return: UserPhoneNumber object or none
        """
        try:
            return self.get(owner=user, is_default=True)
        except UserPhoneNumber.DoesNotExist:
            return None


class UserPhoneNumber(models.Model):
    # uses https://github.com/stefanfoulis/django-phonenumber-field
    number = PhoneNumberField()

    verified = models.BooleanField(
        _('Verified Status'),
        default=False,
        help_text=_('Define if this number have been verified.'),
    )
    __original_verified = None
    is_default = models.BooleanField(
        _('Default Status'),
        default=False,
        help_text=_('Define if this number is users default number.'),
    )
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,
                              related_name='phone_number_obj',
                              on_delete=models.CASCADE)
    created_at = models.DateTimeField(_('Date Created'), auto_now_add=True, null=True, blank=True)
    verified_status_updated_at = models.DateTimeField(null=True, editable=False)

    objects = PhoneNumberManager()

    class Meta:
        db_table = 'user_phone_numbers'
        constraints = [
            models.UniqueConstraint(fields=['number', 'owner'], name='unique_users_phone_number')
        ]
        verbose_name = _('User Phone Numbers')
        verbose_name_plural = _('User Phone Numbers')

    def __init__(self, *args, **kwargs):
        super(UserPhoneNumber, self).__init__(*args, **kwargs)
        self.__original_verified = self.verified

    def save(self, *args, **kwargs):
        # check if there is a change is the verified field
        if self.verified != self.__original_verified:
            # update timestamp
            self.verified_status_updated_at = datetime.now(tz=timezone.utc)

        # check there is no other same number(s) (from another owner) which are also verified,
        # if there are any, set all of them to False, so there is a unique number with `verified=True`,
        # allow exactly single 'verified=True' value per 'number'
        if self.verified:
            UserPhoneNumber.objects.filter(number=self.number, verified=True).update(verified=False)

            # if current owner still does not have any default number (first time a number is saved),
            # this under verified if statement since only verified number should be able default.
            if not UserPhoneNumber.objects.filter(owner=self.owner, is_default=True):
                self.is_default = True

        # check are no multiple numbers, for the same owner (user) which are `is_default=True`,
        # if there are any, set all of them to False, so there is a unique number (per user) with `is_default=True`.
        # allow exactly single 'is_default=True' value per 'owner'
        if self.is_default:
            UserPhoneNumber.objects.filter(owner=self.owner, is_default=True).update(is_default=False)

        # save new verified state to __original_verified for future checks
        self.__original_verified = self.verified
        super(UserPhoneNumber, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.number)

    def get_mobile_number_carrier(self):
        """
        get numbers mobile carrier, return empty string is not found.
        :return: string
        """
        from phonenumbers import carrier, parse
        number = parse(str(self.number))
        return carrier.name_for_number(number, "en")

    def get_number_location_description(self):
        """
        return a text description of a PhoneNumber object, return empty string is not found.
        :return: string
        """
        from phonenumbers import geocoder, parse
        return geocoder.description_for_number(parse(str(self.number)), "en")


class AbstractAddress(models.Model):
    TIMEZONES = tuple(zip(pytz.all_timezones, pytz.all_timezones))

    first_name = models.CharField(_("First name"), max_length=128, validators=[MinLengthValidator(2)])
    last_name = models.CharField(_("Last name"), max_length=128, validators=[MinLengthValidator(2)])

    street_name = models.CharField(_("Street name"), max_length=128,
                                   help_text='Street address, P.O. box, company name, c/o')
    street_number = models.CharField(_("Street number"), max_length=128,
                                     help_text='Apartment, suite, unit, building, floor, etc.')
    city = models.CharField(_("City"), max_length=128)
    state = models.CharField(_("State/County"), max_length=128, null=True, blank=True)

    # uses https://github.com/SmileyChris/django-countries#countryfield
    country = CountryField(_('Country'))
    zip_code = models.IntegerField(_('Zip code'))
    timezone = models.CharField(max_length=32, choices=TIMEZONES, default='UTC')

    created_at = models.DateTimeField(_('Date Created'), auto_now_add=True, blank=True, editable=False)

    class Meta:
        abstract = True
        verbose_name = _('Address')
        verbose_name_plural = _('Addresses')

    def __str__(self):
        if self.state:
            return '{} {} {}, {}, {}, {}'.format(self.street_name,
                                                 self.street_number,
                                                 self.city,
                                                 self.state,
                                                 self.zip_code,
                                                 self.country)
        return '{}, {}, {}, {}, {}'.format(self.street_name,
                                           self.street_number,
                                           self.city,
                                           self.zip_code,
                                           self.country)

    def clean(self):
        # validate zip code is valid for country
        self.validate_zip_code_is_valid_country()

    def validate_zip_code_is_valid_country(self):
        """
        validate zip code is valid code for input country code
        """
        country_code = self.country

        # cast integer zip code to string
        zip_code = str(self.zip_code)
        regex = ZIP_CODES_REGEX.get(country_code, None)

        # Validate postcode against regex for the country if available
        if regex and not re.match(regex, zip_code):
            raise ValidationError(message='Zip Code \'{}\' is not valid for {}'.format(zip_code, self.country.name))


class UserAddressManager(models.Manager):
    def get_all_user_addresses(self, user):
        return self.all().filter(user=user)


class UserAddress(AbstractAddress):
    """
    users address,
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='addresses',
        on_delete=models.CASCADE,
        verbose_name=_('User'))

    default_address = models.BooleanField(
        _('Default address'), default=False,
        help_text=_('Define if this address should be default one')
    )

    default_billing_address = models.BooleanField(
        _('Default billing address'), default=False,
        help_text=_('Define if this should be default billing address')
    )

    phone_number = models.ForeignKey(
        UserPhoneNumber,
        related_name='phone_number',
        on_delete=models.CASCADE,
        verbose_name=_('Phone Number'))

    notes = models.TextField(
        blank=True, verbose_name=_('Instructions'),
        help_text=_("Add anything you need here to let us know."))

    objects = UserAddressManager()

    class Meta:
        db_table = 'user_addresses'
        verbose_name = _("User address")
        verbose_name_plural = _("User addresses")

    def clean(self):
        if hasattr(settings, 'ENFORCE_USER_ADDRESS_VERIFIED_PHONE'):
            if settings.ENFORCE_USER_ADDRESS_VERIFIED_PHONE:
                # try getting self.user, since UserAddress can get created from admin without user reference
                try:
                    users_verified_numbers = UserPhoneNumber.objects.get_verified_phone_numbers_of_user(user=self.user)
                except User.DoesNotExist as e:
                    raise ValidationError(message='{}'.format(e))

                # make sure saved phone number has been verified, and belong to current user saved
                if self.phone_number not in users_verified_numbers:
                    raise ValidationError(message='{} has not been verified.'.format(self.phone_number))

    def save(self, *args, **kwargs):
        # allow exactly single 'default_address=True' value per 'user'
        if self.default_address:
            UserAddress.objects.filter(user=self.user, default_address=True).update(default_address=False)

            # if current user still does not have any default address (first time an address is saved).
            if not UserAddress.objects.filter(user=self.user, default_address=True):
                self.default_address = True

        # allow exactly single 'default_billing_address=True' value per 'user'
        if self.default_billing_address:
            UserAddress.objects.filter(
                user=self.user, default_billing_address=True
            ).update(default_billing_address=False)

        super(UserAddress, self).save(*args, **kwargs)


class UserManager(BaseUserManager):
    def _create_user(self, email, password, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, primary_key=True, validators=[validate_email])
    user_name = models.CharField(_('User Name'), max_length=128, blank=True)
    first_name = models.CharField(_('First Name'), max_length=32, blank=True, validators=[validate_alphabetic_string])
    last_name = models.CharField(_('Last Name'), max_length=32, blank=True, validators=[validate_alphabetic_string])

    USER_GENDER_CHOICES = (
        ('m', 'Male'),
        ('f', 'Female'),
        ('x', 'Not specified'),
    )

    gender = models.CharField(_('Gender'), choices=USER_GENDER_CHOICES, max_length=1, default='x')
    birth_date = models.DateField(_('Birth Date'), null=True, blank=True, validators=[validate_users_min_age])

    linkedin = models.URLField(max_length=255, blank=True)
    facebook = models.URLField(max_length=255, blank=True)
    github = models.URLField(max_length=255, blank=True)
    twitter = models.URLField(max_length=255, blank=True)

    registration_ip = models.GenericIPAddressField('Registered From', null=True)
    language = models.CharField(_('Users Language'), choices=LANGUAGES, max_length=2, default='en')

    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this site.'),
    )
    is_active = models.BooleanField(
        _('Active Status'),
        default=False,
        help_text=_('Define if this user should be treated as active. '),
    )
    date_created = models.DateTimeField(_('Date Created'), auto_now_add=True, blank=True, editable=False)
    last_update_date = models.DateTimeField(auto_now=True, editable=False)
    last_login = models.DateTimeField(default=None, blank=True, null=True, editable=False)
    last_login_ip = models.GenericIPAddressField(_('Logged in from'), default=None, blank=True, null=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        db_table = 'users'

    def __str__(self):
        return self.email

    def get_full_name(self):
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_first_name(self):
        return self.first_name

    def get_last_name(self):
        return self.last_name

    def get_user_addresses(self):
        return self.addresses.get_all_user_addresses(user=self)

    def get_all_phone_numbers(self):
        return self.phone_number_obj.get_all_phone_numbers_of_user(user=self)

    def get_verified_phone_numbers(self):
        return self.phone_number_obj.get_verified_phone_numbers_of_user(user=self)

    def get_verified_phone_numbers_list(self):
        return self.phone_number_obj.get_verified_number_list(user=self)

    def create_verification_email(self):
        self.email_verification_obj.create_verification(email=self.email)

    def send_verification_email(self, subject, body, from_mail):
        self.email_verification_obj.send_verification_email(subject,
                                                            body,
                                                            from_mail,
                                                            self.email)

    def get_uuid_of_email(self):
        return self.email_verification_obj.get_uuid_of_email(self.email)


class DjangoEmailVerifierManger(models.Manager):

    def create_verification(self, email, user=None):
        user = user or getattr(self, 'instance', None)
        if not user:
            raise ValueError('User object must be provided')

        if email not in user.email:
            raise ValueError('Email does not belong to user: %s', user.get_username())
        return self.create(user=user, email=email)

    # @receiver(post_save, sender=DjangoEmailVerifier, dispatch_uid="verify new account")
    # def send_verification_email(sender, instance, signal, *args, **kwargs):
    def send_verification_email(self, subject, body, from_mail, to_mail):
        email_verification_onj = self.all().get(email=to_mail)

        if not email_verification_onj.is_verified:
            send_mail(
                subject,
                body,
                from_mail,
                [email_verification_onj.email],  # To
                fail_silently=False,
            )

        return True

    def get_uuid_of_email(self, email):
        return self.all().get(email=email).verification_uuid


class DjangoEmailVerifier(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             related_name='email_verification_obj',
                             on_delete=models.CASCADE)
    # user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    email = models.EmailField(max_length=255)
    is_verified = models.BooleanField('verified', default=False)
    verification_uuid = models.UUIDField('Unique Verification UUID', default=uuid.uuid4)
    date_created = models.DateTimeField('Date Created', auto_now_add=True, blank=True)
    verified_at = models.DateTimeField(blank=True, null=True)

    objects = DjangoEmailVerifierManger()

    REQUIRED_FIELDS = ['user']

    class Meta:
        verbose_name = _('email verifications')
        verbose_name_plural = _('email verifications')
        db_table = 'email_verifications'

    def __str__(self):
        return 'Email Verification for User: ' + str(self.email)

    def verified(self):
        return self.is_verified

    def uuid_expire_date(self):
        # Only if DJANGO_EMAIL_VERIFIER_EXPIRE_TIME is not None,
        # Else, uuid never expire.
        # Set example: DJANGO_EMAIL_VERIFIER_EXPIRE_TIME=''
        hours_to_expire = getattr(settings, 'DJANGO_EMAIL_VERIFIER_EXPIRE_TIME', None)
        return self.date_created + timedelta(hours=hours_to_expire) if hours_to_expire is not None else None

    def is_uuid_expired(self):
        return timezone.now() >= self.uuid_expire_date()

    def verify_record(self):
        if self.is_uuid_expired():
            raise Exception("UUID {} expired".format(self.verification_uuid))

        # If current object yet verified
        if not self.verified():
            self.is_verified = True
            self.verified_at = timezone.now()
            self.save()
        else:
            raise Exception("email {} already verified".format(self.email))

        # Set account is active status
        self.user.is_active = True
        self.user.save()

        return True
