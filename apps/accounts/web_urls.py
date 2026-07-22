from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from . import web_views
from .forms import StyledAuthenticationForm

app_name = 'accounts'

urlpatterns = [
    path('register/', web_views.register_view, name='register'),
    path(
        'login/',
        LoginView.as_view(template_name='accounts/login.html', authentication_form=StyledAuthenticationForm),
        name='login',
    ),
    path('logout/', LogoutView.as_view(next_page='marketplace:browse'), name='logout'),
    path('profile/edit/', web_views.profile_edit_view, name='profile-edit'),
]
