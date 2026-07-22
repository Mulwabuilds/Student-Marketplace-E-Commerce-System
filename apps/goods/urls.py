from django.urls import path
from . import views

urlpatterns = [
    path('', views.good_list, name='good_list'),
    path('<int:pk>/', views.good_detail, name='good_detail'),
    path('new/', views.good_create, name='good_create'),
    path('<int:pk>/edit/', views.good_update, name='good_update'),
    path('<int:pk>/delete/', views.good_delete, name='good_delete'),
]