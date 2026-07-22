from django.contrib import admin
from .models import Service, ServiceImage


class ServiceImageInline(admin.TabularInline):
    model = ServiceImage
    extra = 1


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'campus_location', 'price', 'is_available', 'created_at')
    list_filter = ('is_available', 'category', 'campus_location')
    search_fields = ('title', 'description')
    inlines = [ServiceImageInline]


@admin.register(ServiceImage)
class ServiceImageAdmin(admin.ModelAdmin):
    list_display = ('service', 'uploaded_at')
