from django.core.management.base import BaseCommand
from django.db import transaction
from apps.core.models import Region, District

from data.districts.districts import DISTRICTS


class Command(BaseCommand):
    help = "Sync districts data from predefined list"

    def handle(self, *args, **options):
        # Get all regions for faster lookup
        regions = {region.id: region for region in Region.objects.all()}

        with transaction.atomic():
            for district_data in DISTRICTS:
                city_id = district_data["city_id"]
                name_uz = district_data["names"]["uz"]
                region_id = district_data["region_id"]

                # Check if region exists
                if region_id not in regions:
                    self.stdout.write(
                        self.style.WARNING(
                            f'Skipping district "{name_uz}" - Region {region_id} not found'
                        )
                    )
                    continue

                # Try to get existing district or create new one
                try:
                    district, created = District.objects.update_or_create(
                        id=city_id,
                        defaults={
                            "name": name_uz,
                            "region": regions[region_id]
                        }
                    )

                    if created:
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'Created district "{name_uz}" in {regions[region_id].name}'
                            )
                        )
                    else:
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'Updated district "{name_uz}" in {regions[region_id].name}'
                            )
                        )

                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f'Error processing district "{name_uz}": {str(e)}'
                        )
                    )

        self.stdout.write(
            self.style.SUCCESS('Successfully synced all districts')
        )
