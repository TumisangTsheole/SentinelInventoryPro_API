from datetime import datetime
from email.policy import default

from django.conf import settings
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=40, blank=False, null=False)
    description = models.CharField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, blank=False, null=False)


class Item(models.Model):
    # Stock Keeping Unit -  a unique identifier for each product in the inventory system
    sku = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey("Category", on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    reorder_threshold = models.IntegerField()
    reorder_quantity = models.IntegerField()
    unit_of_measure = models.CharField(
        max_length=50
    )  # litres, integer units, grams...etc
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(
        auto_now_add=True
    )  # auto_now_add only set timestamp once
    updated_at = models.DateTimeField(
        auto_now=True
    )  # updates every time object is saved !WARNING -> THIS UPDATE ONLY HAPPENS THROUGH THE ORM, NOT THE DB ITSELF
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="items_created",
        on_delete=models.SET_NULL,
        null=True,
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="items_updated",
        on_delete=models.SET_NULL,
        null=True,
    )


class StockMovement(models.Model):
    MOVEMENT_CHOICES = [
        ("IN", "Stock In"),
        ("OUT", "Stock Out"),
        ("ADJUST", "Adjustment"),
    ]

    id = models.AutoField(primary_key=True)
    item = models.ForeignKey("Item", on_delete=models.CASCADE)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_CHOICES)
    quantity_change = models.IntegerField()
    quantity_after = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class RestockAlert(models.Model):
    item = models.ForeignKey("Item", on_delete=models.CASCADE)
    predicted_days_until_zero = models.DecimalField(max_digits=5, decimal_places=2)
    current_quantity = models.IntegerField()
    avg_daily_consumption = models.DecimalField(max_digits=5, decimal_places=2)
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)


# An immutable, chronological record of all actions taken in the system
# CRITICAL: Strict integrity enforced
class AuditLog(models.Model):
    ACTION_CHOICES = [
        ("CREATE", "Created"),
        ("UPDATE", "Updated"),
        ("DELETE", "Deleted"),
    ]

    user_id = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="user_id",  # Prevents from using user.audittrail_set.all()
    )
    item_id = models.ForeignKey(
        'Item',
        on_delete=models.CASCADE,
        related_name="item_id",  # prevents naming conflicts)
    )
    action_type = models.CharField(
        max_length=100, blank=False, choices=ACTION_CHOICES
    )  # (CREATE/UPDATE/DELETE)
    old_values = models.TextField(null=False, blank=False)  # this is gonna be json
    new_values = models.TextField(blank=False, null=False)  # this is gonna be json
    ip_address = models.CharField(
        max_length=45, null=False, blank=False
    )  # max_length=45 enough to support ipv6
    timestamp = models.DateTimeField(auto_now_add=True, null=False, blank=False)


