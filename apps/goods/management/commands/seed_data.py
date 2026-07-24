import base64
from pathlib import Path

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.goods.models import Good, GoodImage
from apps.catalog.models import CampusLocation, Category 

User = get_user_model()

# Generic placeholder image shared across Goods and Services seed data,
# so seeding doesn't depend on network access (GoodImage.image / ServiceImage.image
# are real ImageFields now, not URLs, per Step 2a). Lives in the consolidated
# top-level static/ dir (templates/static were consolidated out of per-app
# dirs this sprint -- see docs/flags.md).
_PLACEHOLDER_PATH = (
    Path(__file__).resolve().parent.parent.parent.parent.parent
    / "static" / "img" / "placeholder.png"
)

class Command(BaseCommand):
    help = 'Seeds the database with initial marketplace dummy data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting database seed...')

        # 1. Create a dummy seller (Using your required Kabarak domain)
        seller, created = User.objects.get_or_create(
            username='test_seller',
            defaults={'email': 'seller@kabarak.ac.ke'}
        )
        if created:
            seller.set_password('password123')
            seller.save()

        # 2. Create Campus Locations
        locations = ['Kabarak Main Campus', 'Nakuru City Campus']
        for loc_name in locations:
            CampusLocation.objects.get_or_create(name=loc_name)

        # 2.5 Create a Category
        # NOTE: was 'Appliances' -- not one of the six categories the paper
        # specifies (Books, Electronics, Clothing, Crafts, Furniture,
        # Services). Fixed to use a canonical one. Run `manage.py
        # seed_categories` for the full canonical set.
        category, _ = Category.objects.get_or_create(name='Electronics')

        # 3. Create a Dummy Listing (Matching the exact model choices)
        good, created = Good.objects.get_or_create(
            title='Mini Fridge - Barely Used',
            seller=seller,
            defaults={
                'description': 'Perfect for a dorm room. Runs quietly.',
                'price': 8500.00,
                'condition': 'used',        # Changed from 'Excellent'
                'status': 'available',      # Changed from 'Active'
                'category': category,
            }
        )

        # 4. Add an Image to the Listing
        if created:
            good_image = GoodImage(good=good)
            good_image.image.save(
                'mini_fridge_placeholder.png',
                ContentFile(_PLACEHOLDER_PATH.read_bytes()),
                save=True,
            )

        self.stdout.write(self.style.SUCCESS('Successfully seeded the database!'))