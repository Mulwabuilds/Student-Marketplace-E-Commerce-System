from django.contrib import admin
from .models import CampusLocation


@admin.register(CampusLocation)
class CampusLocationAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    