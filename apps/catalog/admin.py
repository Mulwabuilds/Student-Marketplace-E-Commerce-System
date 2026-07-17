from django.contrib import admin
from .models import CampusLocation, Category

@admin.register(CampusLocation)
class CampusLocationAdmin(admin.ModelAdmin):
    list_display = ("id", "name")

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "parent_category_id")
    search_fields = ("name",)