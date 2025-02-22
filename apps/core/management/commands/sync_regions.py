from django.core.management.base import BaseCommand
from apps.core.models import Region

from data.regions.regions import REGIONS


class Command(BaseCommand):
    help = "Sync regions data from predefined list"

    def handle(self, *args, **options):
        for region_data in REGIONS:
            region_id = region_data["region_id"]
            name_uz = region_data["names"]["uz"]

            # Try to get existing region or create new one
            region, created = Region.objects.update_or_create(
                id=region_id,
                defaults={
                    "name": name_uz
                }
            )

            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created region "{name_uz}"')
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(f'Updated region "{name_uz}"')
                )

        self.stdout.write(
            self.style.SUCCESS('Successfully synced all regions')
        )
