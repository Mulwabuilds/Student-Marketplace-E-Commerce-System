from django.db import models

from apps.catalog.models import Category, CampusLocation


class Service(models.Model):
    id = models.BigAutoField(primary_key=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="services"
    )
    campus_location = models.ForeignKey(
        CampusLocation,
        on_delete=models.CASCADE,
        related_name="services"
    )
    title = models.CharField(max_length=150)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title


class ServiceImage(models.Model):
    id = models.BigAutoField(primary_key=True)
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name="images"
    )
    image = models.ImageField(upload_to="services/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.service.title}"
