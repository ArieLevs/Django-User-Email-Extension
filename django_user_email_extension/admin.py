from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext_lazy as _

from django_user_email_extension.models import DjangoEmailVerifier, User, Address, PhoneNumber


@admin.register(User)
class UserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'),
         {'fields': ('first_name', 'last_name', 'gender', 'birth_date', 'default_phone_number', 'language')}),
        (_('Address info'), {'fields': ['address']}),
        (_('Social info'), {'fields': ('linkedin', 'facebook', 'github', 'twitter')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2')}
         ),
    )
    list_display = ('email', 'first_name', 'last_name', 'is_active', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    pass


@admin.register(DjangoEmailVerifier)
class UserAdmin(admin.ModelAdmin):
    list_display = ('user', 'email', 'is_verified',)
    list_filter = ('is_verified',)
    ordering = ('user',)
    pass


@admin.register(Address)
class UserAdmin(admin.ModelAdmin):
    list_display = ('street_name', 'street_number', 'city', 'state', 'country', 'zip_code')
    list_filter = ('country',)
    ordering = ('country', 'city', 'street_name',)
    pass


@admin.register(PhoneNumber)
class UserAdmin(admin.ModelAdmin):
    list_display = ('number', 'type', 'verified', 'belongs_to',)
    list_filter = ('type', 'verified',)
    search_fields = ('number', 'belongs_to',)
    ordering = ('number',)
    pass
