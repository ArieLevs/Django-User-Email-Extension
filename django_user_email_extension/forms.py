from django.core.exceptions import ValidationError
from django.forms import Form, ModelForm, TextInput, Select, DateInput, NumberInput, CharField, RadioSelect, ChoiceField
from phonenumbers import is_valid_number, parse, NumberParseException

from django_user_email_extension.models import User, UserAddress, DjangoEmailVerifier


class TokenForm(Form):
    token = CharField(
        widget=TextInput(attrs={'class': 'form-control'}))


class PhoneNumberVerificationForm(Form):
    """
    although this is a Form and not a ModelForm, an instance (PhoneNumber) is passed to init,
    as this form used to create phone numbers, but used separated fields
    bootstrap ready form
    """
    country_code = CharField(widget=TextInput(attrs={'class': 'form-control'}),
                             required=True, help_text='Valid county code, eg +1')
    phone_number = CharField(widget=TextInput(attrs={'class': 'form-control'}))
    confirmation_type = ChoiceField(
        choices=[('sms', 'Send me a text')],
        # initial=sms will set checked radio button to 'sms' value
        widget=RadioSelect(attrs={'class': 'form-check-input'}), initial='sms', required=True)

    # this form should also get 'instance'
    def __init__(self, instance, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']
        if not phone_number.isdigit():
            self.add_error('phone_number', 'Phone number should contain numbers only')
        return phone_number

    def clean_country_code(self):
        country_code = self.cleaned_data['country_code']
        if not country_code.startswith('+'):
            country_code = '+' + country_code
        return country_code

    def clean(self):
        data = self.cleaned_data

        phone_number = data['country_code'] + data['phone_number']
        try:
            phone_number = parse(phone_number, None)
            if not is_valid_number(phone_number):
                self.add_error('phone_number', 'Invalid phone number')
            else:
                # both values are actually cleaned here
                self.cleaned_data['country_code'] = phone_number.country_code
                self.cleaned_data['phone_number'] = phone_number
        except NumberParseException as e:
            self.add_error('phone_number', e)


class UserAddressForm(ModelForm):
    """
    bootstrap ready form
    """

    class Meta:
        model = UserAddress
        exclude = ['timezone']
        widgets = {
            'first_name': TextInput(attrs={'class': 'form-control'}),
            'last_name': TextInput(attrs={'class': 'form-control'}),
            'street_name': TextInput(attrs={'class': 'form-control'}),
            'street_number': TextInput(attrs={'class': 'form-control'}),
            'city': TextInput(attrs={'class': 'form-control'}),
            'state': TextInput(attrs={'class': 'form-control'}),
            'country': Select(attrs={'class': 'form-control'}),
            'zip_code': NumberInput(attrs={'class': 'form-control'}),
            'phone_number': Select(attrs={'class': 'form-control'}),
            'notes': TextInput(attrs={'class': 'form-control'}),
        }

        fields = [
            'first_name', 'last_name',
            'street_name', 'street_number', 'city', 'state', 'country', 'zip_code',
            'phone_number', 'notes',
        ]

    # this form should also get 'user' instance
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance.user = user

        # since 'phone_number' field is a foreign key to UserPhoneNumber model, for will allow to choose from all users,
        # make sure the 'phone_number' will have only current users phone numbers
        self.fields['phone_number'].queryset = user.get_all_phone_numbers()

    def clean(self):
        # empty clean function so model will not block a user of attempt to add an already existing address
        return self.cleaned_data


class UserProfileForm(ModelForm):
    """
    bootstrap ready form
    """

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'gender', 'birth_date', 'language']
        widgets = {
            'first_name': TextInput(attrs={'class': 'form-control'}),
            'last_name': TextInput(attrs={'class': 'form-control'}),
            'gender': Select(attrs={'class': 'form-control'}),
            'birth_date': DateInput(attrs={
                'class': 'form-control datetimepicker-input',
                'data-target': '#datetimepicker1',
                'type': 'text'
            }),
            'language': Select(attrs={'class': 'form-control'}),
        }

    # # override init function, so it will also get a 'user' key,
    # def __init__(self, *args, **kwargs):
    #     super(UserProfileForm, self).__init__(*args, **kwargs)

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if not first_name:
            raise ValidationError(message='First name cannot be empty')
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if not last_name:
            raise ValidationError(message='Last name cannot be empty')
        return last_name

    def clean_birth_date(self):
        birth_date = self.cleaned_data.get('birth_date')
        if birth_date is None:
            raise ValidationError(message='Birth Date must be set')
        return birth_date


class VerificationUUIDForm(ModelForm):
    class Meta:
        model = DjangoEmailVerifier
        fields = ['email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def full_clean(self):
        return super().full_clean()
