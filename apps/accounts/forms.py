from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import User, Profile


class StyledAuthenticationForm(AuthenticationForm):
    """
    Bootstrap-styled wrapper around Django's built-in AuthenticationForm.
    Still uses django.contrib.auth.views.LoginView untouched (Step 3 says no
    custom views) -- just passed in via authentication_form=.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')

    def clean_email(self):
        email = self.cleaned_data['email']
        if not email.lower().endswith('@kabarak.ac.ke'):
            raise forms.ValidationError('Email must be a @kabarak.ac.ke address.')
        return email


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['campus_location', 'phone_number', 'bio', 'profile_photo_url', 'is_open']
        widgets = {
            'campus_location': forms.Select(attrs={'class': 'form-select'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'profile_photo_url': forms.URLInput(attrs={'class': 'form-control'}),
            'is_open': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
