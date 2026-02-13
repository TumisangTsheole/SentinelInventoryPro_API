from rest_framework import serializers
from . import models

class CategorySerializer(serializers.ModelSerializer):
	class Meta:
		model = models.Category
		fields = ['id', 'name', 'description', 'created_at', 'updated_at']

class ItemSerializer(serializers.ModelSerializer):
	class Meta:
		model = models.Item
		fields = ['id', 'sku', 'name', 'description', 'category', 'price', 'quantity', 'reorder_threshold', 'reorder_quantity', 'unit_of_measure', 'is_active', 'created_at', 'updated_at', 'created_by', 'updated_by']
