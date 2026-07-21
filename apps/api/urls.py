from django.urls import path, include
from .views import api_root, service_list

urlpatterns = [
    path("", api_root, name="api-root"),
    # T10/T11/T12/T13 routes get added here as they're built
    path("goods/", include("apps.goods.urls")),
    path("services/", service_list, name="service-list"),
    path("accounts/", include("apps.accounts.urls")),
]
