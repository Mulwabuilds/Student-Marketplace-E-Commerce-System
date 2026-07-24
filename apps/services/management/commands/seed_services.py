from pathlib import Path

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.services.models import Service, ServiceImage
from apps.catalog.models import CampusLocation, Category

User = get_user_model()

_PLACEHOLDER_PATH = (
    Path(__file__).resolve().parent.parent.parent.parent.parent
    / "static" / "img" / "placeholder.png"
)


class Command(BaseCommand):
    help = "Seeds the database with a demo Service listing (mirrors apps/goods/management/commands/seed_data.py)."

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding demo service...")

        seller, created = User.objects.get_or_create(
            username="test_seller",
            defaults={"email": "seller@kabarak.ac.ke"},
        )
        if created:
            seller.set_password("password123")
            seller.save()

        location, _ = CampusLocation.objects.get_or_create(name="Kabarak Main Campus")
        category, _ = Category.objects.get_or_create(name="Services")

        service, created = Service.objects.get_or_create(
            title="Laundry Pickup & Fold",
            seller=seller,
            defaults={
                "description": "Same-day laundry service for busy students. Pickup and drop-off at your hostel.",
                "price": 250.00,
                "is_available": True,
                "category": category,
                "campus_location": location,
            },
        )

        if created:
            service_image = ServiceImage(service=service)
            service_image.image.save(
                "laundry_placeholder.png",
                ContentFile(_PLACEHOLDER_PATH.read_bytes()),
                save=True,
            )

        self.stdout.write(self.style.SUCCESS("Successfully seeded a demo service!"))
