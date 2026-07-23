from django import forms
from .models import Service


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