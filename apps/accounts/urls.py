from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.register, name="register"),
    path("verify-otp/", views.verify_otp_view, name="verify-otp"),
]