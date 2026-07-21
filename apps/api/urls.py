from django.urls import path, include
from .views import api_root, service_list

urlpatterns = [
    path("", api_root, name="api-root"),
    path("services/", service_list, name="service-list"),
    path("accounts/", include("apps.accounts.urls")),
]