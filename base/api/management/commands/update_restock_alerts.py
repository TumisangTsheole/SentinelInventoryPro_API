from django.core.management.base import BaseCommand
from django.utils import timezone
from api.models import Item, RestockAlert

class Command(BaseCommand):
    help = 'Update restock alerts based on current stock levels and consumption'

    def handle(self, *args, **options):
        # Delete all unresolved alerts (we'll recreate fresh)
        deleted_count, _ = RestockAlert.objects.filter(is_resolved=False).delete()
        self.stdout.write(f"Deleted {deleted_count} old unresolved alerts")

        created_count = 0
        for item in Item.objects.filter(is_active=True):
            avg_consumption = item.get_average_daily_consumption()
            if avg_consumption <= 0:
                continue  # No consumption data, skip

            days_until_zero = item.predicted_days_until_zero()
            if days_until_zero is None:
                continue

            if days_until_zero <= 14:
                RestockAlert.objects.create(
                    item=item,
                    predicted_days_until_zero=round(days_until_zero, 1),
                    current_quantity=item.quantity,
                    avg_daily_consumption=round(avg_consumption, 2),
                    is_resolved=False,
                    created_at=timezone.now()
                )
                created_count += 1

        self.stdout.write(self.style.SUCCESS(f"Created {created_count} new restock alerts"))
