import random
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone
from datetime import timedelta

OTP_VALIDITY_MINUTES = 10


def generate_otp():
    """Returns a 6-digit numeric OTP as a string."""
    return f"{random.randint(0, 999999):06d}"


def set_otp_for_user(user):
    """Generates an OTP, hashes it, sets expiry, saves the user."""
    otp = generate_otp()
    user.otp_code_hash = make_password(otp)
    user.otp_expires_at = timezone.now() + timedelta(minutes=OTP_VALIDITY_MINUTES)
    user.save(update_fields=["otp_code_hash", "otp_expires_at"])
    return otp  # plaintext, only for sending — never stored


def verify_otp(user, submitted_code):
    """Returns True/False. Does not clear fields — caller decides when."""
    if not user.otp_code_hash or not user.otp_expires_at:
        return False
    if timezone.now() > user.otp_expires_at:
        return False
    return check_password(submitted_code, user.otp_code_hash)
