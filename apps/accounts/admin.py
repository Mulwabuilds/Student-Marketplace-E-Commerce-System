from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Profile


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False


class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Verification", {"fields": ("is_email_verified", "otp_code_hash", "otp_expires_at")}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("Required", {"fields": ("email",)}),
    )
    list_display = ("username", "email", "is_email_verified", "is_staff")


admin.site.register(User, UserAdmin)
