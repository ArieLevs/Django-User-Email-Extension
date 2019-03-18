
from django.contrib import admin
from django_user_email_extension.models import DjangoEmailVerifier, User
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext_lazy as _


@admin.register(User)
class UserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'birth_date', 'phone_number', 'language')}),
        (_('Location info'), {'fields': ('address', 'city', 'country', 'postal_code')}),
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
