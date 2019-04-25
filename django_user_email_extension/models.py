import uuid
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from django.db import models
from django.core.mail import send_mail

from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin

from django_user_email_extension.validators import phone_number_validator


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
    email = models.EmailField(unique=True, primary_key=True)
    user_name = models.CharField(_('User Name'), max_length=128, blank=True)
    first_name = models.CharField(_('First Name'), max_length=32, blank=True)
    last_name = models.CharField(_('Last Name'), max_length=32, blank=True)

    address = models.TextField(max_length=500, default='', blank=True)
    city = models.CharField(max_length=30, default='', blank=True)
    country = models.CharField(max_length=30, default='', blank=True)
    postal_code = models.IntegerField(blank=True, default=00000)

    birth_date = models.DateField(null=True, blank=True)
    phone_number = models.CharField(validators=[phone_number_validator()],
                                    max_length=17,
                                    blank=True)

    linkedin = models.URLField(max_length=255, blank=True)
    facebook = models.URLField(max_length=255, blank=True)
    github = models.URLField(max_length=255, blank=True)
    twitter = models.URLField(max_length=255, blank=True)

    registration_ip = models.GenericIPAddressField('Registered From', null=True)
    language = models.CharField(_('Users Language'), max_length=2, null=False, default='EN')

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
    date_created = models.DateTimeField('Date Created', auto_now_add=True, blank=True)
    last_update_date = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(default=None, blank=True, null=True)
    last_login_ip = models.GenericIPAddressField('Logged in from', default=None, blank=True, null=True)

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


def verify_record(uuid_value):
    # If input UUID exist in the db
    try:
        email_ver_object = DjangoEmailVerifier.objects.get(verification_uuid=uuid_value, is_verified=False)
    except DjangoEmailVerifier.DoesNotExist:
        raise Exception("Error - %s not associated to any email" % uuid_value)

    if email_ver_object.is_uuid_expired():
        raise Exception("Error - %s expired" % uuid_value)

    # If current object yet verified
    if not email_ver_object.verified():
        email_ver_object.is_verified = True
        email_ver_object.verified_at = timezone.now()
        email_ver_object.save()

    # Set account is active status
    email_ver_object.user.is_active = True
    email_ver_object.user.save()

    return True
