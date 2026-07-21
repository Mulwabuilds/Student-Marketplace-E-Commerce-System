from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth import get_user_model

from .serializers import RegisterSerializer
from .utils import set_otp_for_user, verify_otp

User = get_user_model()


@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()

    otp = set_otp_for_user(user)
    # No email backend wired up yet — printing for now so you can test the flow.
    # T10 acceptance criteria doesn't require real email delivery, just that
    # a hashed OTP + expiry gets generated correctly.
    print(f"[DEV ONLY] OTP for {user.email}: {otp}")

    return Response(
        {"message": "Registered. Check your email for the OTP."},
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def verify_otp_view(request):
    email = request.data.get("email")
    code = request.data.get("otp")

    if not email or not code:
        return Response({"error": "email and otp are required."}, status=400)

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({"error": "Invalid email."}, status=400)

    if not verify_otp(user, code):
        return Response({"error": "Invalid or expired OTP."}, status=400)

    user.is_email_verified = True
    user.otp_code_hash = None
    user.otp_expires_at = None
    user.save(update_fields=["is_email_verified", "otp_code_hash", "otp_expires_at"])

    return Response({"message": "Email verified successfully."})
