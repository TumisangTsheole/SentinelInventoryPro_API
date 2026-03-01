from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from api.models import Item, Category, StockMovement, RestockAlert, AuditLog

class Command(BaseCommand):
    help = 'Setup groups and permissions'

    def handle(self, *args, **options):
        # Define groups
        viewer_group, _ = Group.objects.get_or_create(name='Viewer')
        stocker_group, _ = Group.objects.get_or_create(name='Stocker')
        admin_group, _ = Group.objects.get_or_create(name='Admin')

        # Get content types for our models
        item_ct = ContentType.objects.get_for_model(Item)
        category_ct = ContentType.objects.get_for_model(Category)
        stock_ct = ContentType.objects.get_for_model(StockMovement)
        alert_ct = ContentType.objects.get_for_model(RestockAlert)
        audit_ct = ContentType.objects.get_for_model(AuditLog)

        # Define permissions
        # Viewer: can view all (list and retrieve) – i.e., view permissions
        view_permissions = [
            Permission.objects.get(content_type=item_ct, codename='view_item'),
            Permission.objects.get(content_type=category_ct, codename='view_category'),
            Permission.objects.get(content_type=stock_ct, codename='view_stockmovement'),
            Permission.objects.get(content_type=alert_ct, codename='view_restockalert'),
            Permission.objects.get(content_type=audit_ct, codename='view_auditlog'),
        ]
        viewer_group.permissions.add(*view_permissions)

        # Stocker: viewer + add/change for Item, Category, StockMovement
        stocker_permissions = list(viewer_group.permissions.all())
        stocker_permissions.extend([
            Permission.objects.get(content_type=item_ct, codename='add_item'),
            Permission.objects.get(content_type=item_ct, codename='change_item'),
            Permission.objects.get(content_type=category_ct, codename='add_category'),
            Permission.objects.get(content_type=category_ct, codename='change_category'),
            Permission.objects.get(content_type=stock_ct, codename='add_stockmovement'),
            Permission.objects.get(content_type=stock_ct, codename='change_stockmovement'),
            # Stocker can also view and resolve alerts (maybe add/change not needed)
        ])
        stocker_group.permissions.set(stocker_permissions)

        # Admin: all permissions for all models (including delete)
        admin_group.permissions.add(*Permission.objects.all())  # or filter by app

        self.stdout.write(self.style.SUCCESS('Groups and permissions created'))
