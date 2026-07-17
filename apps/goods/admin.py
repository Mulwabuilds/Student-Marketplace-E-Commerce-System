from django.contrib import admin
from .models import Good, GoodImage

class GoodImageInline(admin.TabularInline):
    model = GoodImage
    extra = 1
    max_num = 15  # Enforces the cap in the admin interface

@admin.register(Good)
class GoodAdmin(admin.ModelAdmin):
    list_display = ('title', 'seller', 'category', 'price', 'condition', 'status', 'created_at')
    list_filter = ('condition', 'status', 'category')
    search_fields = ('title', 'description')
    inlines = [GoodImageInline]

@admin.register(GoodImage)
class GoodImageAdmin(admin.ModelAdmin):
    list_display = ('good', 'uploaded_at')
