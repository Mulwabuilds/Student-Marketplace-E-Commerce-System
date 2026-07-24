import io

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from PIL import Image, ImageDraw, ImageFont

from apps.accounts.models import Profile
from apps.catalog.models import Category, CampusLocation
from apps.goods.models import Good, GoodImage
from apps.services.models import Service, ServiceImage

User = get_user_model()

# Distinct background colour per category so items visually differ at a glance
_CATEGORY_COLORS = {
    "Books": (99, 91, 255),
    "Electronics": (0, 149, 246),
    "Clothing": (255, 92, 141),
    "Crafts": (255, 159, 28),
    "Furniture": (99, 179, 118),
    "Services": (217, 119, 6),
}

_DEMO_SELLERS = [
    {"username": "wanjiru_m", "email": "wanjiru.m@kabarak.ac.ke", "phone": "254712000001", "bio": "Selling stuff I don't need anymore + doing tutoring on the side."},
    {"username": "otieno_k", "email": "otieno.k@kabarak.ac.ke", "phone": "254712000002", "bio": "SSET student. Fixing phones and PCs for extra cash."},
    {"username": "achieng_n", "email": "achieng.n@kabarak.ac.ke", "phone": "254712000003", "bio": "Crafts, braiding, and the occasional second-hand find."},
]

_GOODS = [
    ("Calculus Textbook (3rd Edition)", "Books", "used", 650, "Stewart's Calculus, some highlighting but binding is solid."),
    ("Wireless Mouse", "Electronics", "new", 800, "Still in the box, bought the wrong one for my laptop."),
    ("Kabarak Hoodie - Size M", "Clothing", "new", 1200, "Never worn, tags still on."),
    ("Handmade Beaded Necklace", "Crafts", "new", 500, "Made these myself, one of a kind."),
    ("Study Desk with Drawer", "Furniture", "used", 3500, "Solid wood, one drawer, minor scuff on one leg."),
    ("Bluetooth Speaker", "Electronics", "used", 1500, "Great bass, battery still lasts ~6 hours."),
    ("Second-hand Novels Bundle (5 books)", "Books", "used", 700, "Mix of fiction, all in good condition."),
    ("Plastic Study Chair", "Furniture", "used", 900, "Sturdy, just need it gone before I move out."),
]

_SERVICES = [
    ("Math & Physics Tutoring", 300, "One-on-one or small group sessions, first-year and second-year units."),
    ("Laundry Pickup & Fold", 250, "Same-day service for busy students. Pickup and drop-off at your hostel."),
    ("Hair Braiding", 400, "Cornrows, box braids, and simple styles. Book ahead on weekends."),
    ("Phone Screen Repair", 600, "Most common Android/iPhone models, usually done same day."),
    ("Graphic Design for Posters/Flyers", 500, "Event posters, flyers, social media graphics -- quick turnaround."),
    ("Room Cleaning Service", 350, "Deep clean for hostel rooms, bring your own detergent for a discount."),
    ("Typing & Printing Assistance", 100, "CAT/assignment typing, formatting, and printing at the library."),
    ("Photography for Events", 1000, "Graduation shoots, small events, digital delivery within 48 hours."),
]


def _generate_image(title, color):
    """Generates a simple, distinct placeholder photo per listing -- a
    coloured card with the item's title on it -- so seeded listings don't
    all share one identical grey box."""
    img = Image.new("RGB", (640, 480), color=color)
    draw = ImageDraw.Draw(img)
    draw.rectangle([10, 10, 629, 469], outline=(255, 255, 255), width=3)
    font = ImageFont.load_default()
    # crude word-wrap so long titles don't run off the image
    words = title.split()
    lines, current = [], ""
    for word in words:
        trial = f"{current} {word}".strip()
        if len(trial) > 22:
            lines.append(current)
            current = word
        else:
            current = trial
    lines.append(current)

    total_h = len(lines) * 18
    y = (480 - total_h) / 2
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        w = bbox[2] - bbox[0]
        draw.text(((640 - w) / 2, y), line, fill=(255, 255, 255), font=font)
        y += 22

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


class Command(BaseCommand):
    help = "Seeds several realistic Goods and Services, each with a real generated image, so the marketplace looks populated."

    def handle(self, *args, **options):
        location = CampusLocation.objects.first()
        if not location:
            self.stdout.write(self.style.ERROR("No CampusLocation rows found -- run `manage.py seed_catalog` first."))
            return

        sellers = []
        for data in _DEMO_SELLERS:
            user, created = User.objects.get_or_create(
                username=data["username"],
                defaults={"email": data["email"], "is_email_verified": True},
            )
            if created:
                user.set_password("password123")
                user.save()
            profile, _ = Profile.objects.get_or_create(user=user)
            profile.phone_number = data["phone"]
            profile.bio = data["bio"]
            profile.is_open = True
            profile.campus_location = location
            profile.save()
            sellers.append(user)

        created_goods = 0
        for i, (title, cat_name, condition, price, description) in enumerate(_GOODS):
            category, _ = Category.objects.get_or_create(name=cat_name)
            good, created = Good.objects.get_or_create(
                title=title,
                defaults={
                    "seller": sellers[i % len(sellers)],
                    "description": description,
                    "price": price,
                    "condition": condition,
                    "status": "available",
                    "category": category,
                },
            )
            if created:
                created_goods += 1
                image_bytes = _generate_image(title, _CATEGORY_COLORS.get(cat_name, (120, 120, 120)))
                good_image = GoodImage(good=good)
                good_image.image.save(f"{good.pk}_demo.png", ContentFile(image_bytes), save=True)

        created_services = 0
        for i, (title, price, description) in enumerate(_SERVICES):
            category, _ = Category.objects.get_or_create(name="Services")
            service, created = Service.objects.get_or_create(
                title=title,
                defaults={
                    "seller": sellers[i % len(sellers)],
                    "description": description,
                    "price": price,
                    "is_available": True,
                    "category": category,
                    "campus_location": location,
                },
            )
            if created:
                created_services += 1
                image_bytes = _generate_image(title, _CATEGORY_COLORS["Services"])
                service_image = ServiceImage(service=service)
                service_image.image.save(f"{service.pk}_demo.png", ContentFile(image_bytes), save=True)

        self.stdout.write(self.style.SUCCESS(
            f"Seeded {created_goods} new goods and {created_services} new services "
            f"(already-existing titles were left untouched, safe to re-run)."
        ))
        