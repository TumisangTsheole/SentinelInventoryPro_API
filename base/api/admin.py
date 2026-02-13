from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.Category)
admin.site.register(models.Item)
admin.site.register(models.StockMovement)
admin.site.register(models.RestockAlert)
admin.site.register(models.AuditLog)

