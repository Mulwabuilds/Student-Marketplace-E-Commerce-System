from django.urls import path
from . import views

app_name = 'marketplace'

urlpatterns = [
    path('', views.browse, name='browse'),
    path('dashboard/', views.dashboard, name='dashboard'),
]
