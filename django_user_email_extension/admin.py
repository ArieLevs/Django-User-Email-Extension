
from django.contrib import admin
from django_user_email_extension.models import DjangoEmailVerifier, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass


@admin.register(DjangoEmailVerifier)
class UserAdmin(admin.ModelAdmin):
    pass
