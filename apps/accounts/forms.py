from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import User, Profile


class StyledAuthenticationForm(AuthenticationForm):
    """
    Still uses django.contrib.auth.views.LoginView untouched (Step 3 says no
    custom views) -- just passed in via authentication_form=. No widget
    classes needed: static/css/main.css styles bare <input> elements
    directly by tag/type selector.
    """
    pass


class RegistrationForm(UserCreationForm):
    """
    Template-based registration for the MVP demo: no OTP step. The DB has a
    CheckConstraint enforcing the @kabarak.ac.ke domain already, but we also
    reject it here so the user gets a clean form error instead of a raw
    IntegrityError bubbling up from the database.
    """

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data['email']
        if not email.lower().endswith('@kabarak.ac.ke'):
            raise forms.ValidationError('Email must be a @kabarak.ac.ke address.')
        return email


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['campus_location', 'phone_number', 'bio', 'profile_photo', 'is_open']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
        }
