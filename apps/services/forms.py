from django import forms
from .models import Service, ServiceImage


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = [
            "category",
            "campus_location",
            "title",
            "description",
            "price",
            "is_available",
        ]


class ServiceImageForm(forms.ModelForm):
    """New: there was no way to attach a photo to a service (no form, no
    route). Mirrors apps/goods/forms.py::GoodImageForm."""
    class Meta:
        model = ServiceImage
        fields = ['image']