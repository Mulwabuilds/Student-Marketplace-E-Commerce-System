from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.goods.models import Good, GoodImage
from apps.catalog.models import CampusLocation, Category 

User = get_user_model()

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
        category, _ = Category.objects.get_or_create(name='Appliances')

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
            GoodImage.objects.create(
                good=good, 
                image_url='https://dummyimage.com/600x400/000/fff&text=Mini+Fridge'
            )

        self.stdout.write(self.style.SUCCESS('Successfully seeded the database!'))