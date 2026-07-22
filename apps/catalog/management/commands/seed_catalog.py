from django.core.management.base import BaseCommand
from apps.catalog.models import CampusLocation

class Command(BaseCommand):
    help = 'Seeds the database with real Kabarak University campus locations'

    def handle(self, *args, **kwargs):
        # Real Kabarak University locations for the marketplace
        locations = [
            "Main Gate",
            "University Library",
            "Student Centre / Mess",
            "School of Science, Engineering and Technology (SSET)",
            "School of Business and Economics Block",
            "School of Law Block",
            "School of Music and Media Block",
            "Oloika Hostel",
            "Oloishobor Hostel",
            "Victoria Hostel",
            "Tugen Hostel",
            "Bogoria Hostel",
            "Baringo Hostel",
            "Elgon Hostel",
            "Serengeti Hostel",
            "Ruwenzori Hostel"
        ]

        self.stdout.write("Clearing old location placeholders...")
        CampusLocation.objects.all().delete()

        self.stdout.write("Seeding real campus locations...")
        for loc_name in locations:
            CampusLocation.objects.create(name=loc_name)
            
        self.stdout.write(self.style.SUCCESS(f'Successfully seeded {len(locations)} campus locations!'))