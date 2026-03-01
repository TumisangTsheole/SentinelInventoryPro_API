from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core import serializers
from crum import get_current_user, get_current_request
import json

from .models import Item, Category, StockMovement, AuditLog

def get_client_ip(request):
    """Extract IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def serialize_instance(instance):
    """Convert model instance to JSON string"""
    return serializers.serialize('json', [instance])

def log_action(sender, instance, action, **kwargs):
    """Generic audit log creator"""
    user = get_current_user()
    request = get_current_request()
    ip = get_client_ip(request) if request else '0.0.0.0'
    
    # Determine old/new values
    if action == 'CREATE':
        old_values = '{}'
        new_values = serialize_instance(instance)
    elif action == 'UPDATE':
        # for update, we need the old state. We can get it from the database
        # but instance already has old values? instance is the updated one.
        # to get old values, we need to fetch pre-save state. With signals, it's tricky.
        # to keep it simple: for update, store only new values and a note.
        old_values = '{}'
        new_values = serialize_instance(instance)
    elif action == 'DELETE':
        old_values = serialize_instance(instance)
        new_values = '{}'
    
    AuditLog.objects.create(
        user_id=user,
        item_id=instance if isinstance(instance, Item) else None,
        action_type=action,
        old_values=old_values,
        new_values=new_values,
        ip_address=ip
    )

# Connect signals for each model
@receiver(post_save, sender=Item)
def item_post_save(sender, instance, created, **kwargs):
    action = 'CREATE' if created else 'UPDATE'
    log_action(sender, instance, action, **kwargs)

@receiver(post_delete, sender=Item)
def item_post_delete(sender, instance, **kwargs):
    log_action(sender, instance, 'DELETE', **kwargs)

# Repeat for Category and StockMovement
@receiver(post_save, sender=Category)
def category_post_save(sender, instance, created, **kwargs):
    action = 'CREATE' if created else 'UPDATE'
    log_action(sender, instance, action, **kwargs)

@receiver(post_delete, sender=Category)
def category_post_delete(sender, instance, **kwargs):
    log_action(sender, instance, 'DELETE', **kwargs)

@receiver(post_save, sender=StockMovement)
def stockmovement_post_save(sender, instance, created, **kwargs):
    action = 'CREATE' if created else 'UPDATE'
    log_action(sender, instance, action, **kwargs)

@receiver(post_delete, sender=StockMovement)
def stockmovement_post_delete(sender, instance, **kwargs):
    log_action(sender, instance, 'DELETE', **kwargs)
