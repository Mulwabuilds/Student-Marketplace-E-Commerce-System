from django.core.management.base import BaseCommand
from apps.catalog.models import Category


class Command(BaseCommand):
    help = "Seeds the six canonical Category rows exactly as named in the research paper (Section 3.6.5)."

    # Matches the wording in docs/STUDENT_MARKETPLACE_RESEARCH_PAPER.docx and
    # docs/TEAM PROJECT RESEARCH PAPER.docx verbatim: "Books, Electronics,
    # Clothing, Crafts, Furniture, and Services." Confirmed via direct text
    # extraction, not guessed.
    CATEGORIES = ["Books", "Electronics", "Clothing", "Crafts", "Furniture", "Services"]

    def handle(self, *args, **options):
        created_count = 0
        for name in self.CATEGORIES:
            _, created = Category.objects.get_or_create(name=name)
            if created:
                created_count += 1

        extras = Category.objects.exclude(name__in=self.CATEGORIES)
        if extras.exists():
            self.stdout.write(self.style.WARNING(
                f"Found {extras.count()} Category row(s) not in the paper's list: "
                f"{list(extras.values_list('name', flat=True))} -- left alone, review manually."
            ))

        self.stdout.write(self.style.SUCCESS(
            f"Seeded {created_count} new categories; {len(self.CATEGORIES)} canonical categories now present."
        ))
