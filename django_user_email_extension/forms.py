from django.core.exceptions import ValidationError
from django.forms import ModelForm, TextInput, Select, DateInput

from django_user_email_extension.models import User


class UserProfileForm(ModelForm):
    """
    bootstrap ready form
    """

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'default_phone_number',
                  'gender', 'birth_date', 'language']
        widgets = {
            'first_name': TextInput(attrs={'class': 'form-control'}),
            'last_name': TextInput(attrs={'class': 'form-control'}),
            'default_phone_number': Select(attrs={'class': 'form-control'}),
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
