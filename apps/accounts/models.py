from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from apps.catalog.models import CampusLocation


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )   # this makes sure that when the user is deleted the profile goes too
    campus_location = models.ForeignKey(
        CampusLocation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="profiles",
    )
    phone_number = models.CharField(max_length=20, blank=True)
    bio = models.TextField(blank=True)
    profile_photo_url = models.URLField(max_length=500, blank=True)
    is_open = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s profile"


# username, password, first_name, last_name, is_staff, is_active, is_superuser, last_login, date_joined imported from AbstractUser
class User(AbstractUser):
    email = models.EmailField(unique=True)
    otp_code_hash = models.CharField(max_length=255, null=True, blank=True)
    otp_expires_at = models.DateTimeField(null=True, blank=True)
    is_email_verified = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(email__iregex=r"@kabarak\.ac\.ke$"),
                name="email_must_be_kabarak_domain",
            )
        ]

    def __str__(self):
        return self.username
    