from django.urls import path
from .views import api_root

urlpatterns = [
    path("", api_root, name="api-root"),
    # T10/T11/T12/T13 routes get added here as they're built
]