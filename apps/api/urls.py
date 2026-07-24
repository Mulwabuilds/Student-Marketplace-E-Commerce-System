from django.urls import path, include
from .views import api_root, service_list

urlpatterns = [
    path("", api_root, name="api-root"),
    # NOTE: apps.goods.urls is template views (good_list/good_detail/etc), not
    # a DRF router -- including it here duplicates the real /goods/ mount in
    # SMES/urls.py and causes reverse('good_detail') to sometimes resolve to
    # /api/goods/N/ instead of /goods/N/. Removed (this is the second time
    # this crept back in via a merge -- see docs/flags.md).
    path("services/", service_list, name="service-list"),
    path("accounts/", include("apps.accounts.urls")),
]
