from rest_framework import serializers
from . import models
from django.contrib.auth.models import User
from django.utils import timezone

# ---------------------------------------------------------------------------- #
#                                        CATEGORY                                      #
# ---------------------------------------------------------------------------- #
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Category
        fields = ['name', 'description']

    # Field level validation
    def validate_name(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("Length of name cannot be less than 3 characters")
        return value    
        
    # Cross field validation for business logic
    def validate(self, data):
        name = data.get('name')
        description = data.get('description')

        if name and description and name == description:
            raise serializers.ValidationError({
                'description': 'description cannot be the same as name'
            })

        # Case 1: CREATE operation (no instance yet)
        if not self.instance:
            if models.Category.objects.filter(name=name).exists():
                raise serializers.ValidationError({
                    'name': 'A category with this name already exists'
                })

        # Case 2: UPDATE operation
        else:
            if 'name' in data and data['name'] != self.instance.name:
                if models.Category.objects.filter(
                    name=data['name']
                ).exclude(id=self.instance.id).exists():
                    raise serializers.ValidationError({
                        'name': 'Another category already has this name'
                    })    

        return data        


# ---------------------------------------------------------------------------- #
#                                          ITEM                                          #
# ---------------------------------------------------------------------------- #
class ItemSerializer(serializers.ModelSerializer):
    # Nested field to show category details in responses
    category_detail = CategorySerializer(source='category', read_only=True)
    
    class Meta:
        model = models.Item
        fields = [
            'sku', 'name', 'description', 'category', 'category_detail',
            'price', 'quantity', 'reorder_threshold', 'reorder_quantity',
            'unit_of_measure', 'is_active'
        ]

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0")
        return value

    def validate_quantity(self, value):
        if value < 0:
            raise serializers.ValidationError("Quantity cannot be negative")
        return value

    def validate_reorder_threshold(self, value):
        if value < 0:
            raise serializers.ValidationError("Reorder threshold cannot be negative")
        return value

    def validate_reorder_quantity(self, value):
        if value < 0:
            raise serializers.ValidationError("Reorder quantity cannot be negative")
        return value

    def validate(self, data):
        sku = data.get('sku')
        quantity = data.get('quantity')
        reorder_threshold = data.get('reorder_threshold')

        # SKU uniqueness check
        if sku:
            # CREATE
            if not self.instance:
                if models.Item.objects.filter(sku=sku).exists():
                    raise serializers.ValidationError({
                        'sku': 'An item with this SKU already exists'
                    })
            # UPDATE
            else:
                if 'sku' in data and data['sku'] != self.instance.sku:
                    if models.Item.objects.filter(
                        sku=data['sku']
                    ).exclude(id=self.instance.id).exists():
                        raise serializers.ValidationError({
                            'sku': 'This SKU already exists'
                        })
            
        return data


# ---------------------------------------------------------------------------- #
#                                  STOCK MOVEMENT                                    #
# ---------------------------------------------------------------------------- #
class StockMovementSerializer(serializers.ModelSerializer):
    # Show related data in responses
    item_detail = ItemSerializer(source='item', read_only=True)
    user_detail = serializers.StringRelatedField(source='user', read_only=True)
    
    class Meta:
        model = models.StockMovement
        fields = [
            'id', 'item', 'item_detail', 'user', 'user_detail',
            'movement_type', 'quantity_change', 'quantity_after',
            'reason', 'notes', 'created_at'
        ]
        read_only_fields = ['quantity_after', 'created_at']

    def validate_quantity_change(self, value):
        if value == 0:
            raise serializers.ValidationError("Quantity change cannot be zero")
        return value

    def validate(self, data):
        item = data.get('item')
        movement_type = data.get('movement_type')
        quantity_change = data.get('quantity_change', 0)
        
        # Only validate stock levels if we have an item
        if item and movement_type and quantity_change:
            # Stock OUT validation
            if movement_type == 'OUT' and abs(quantity_change) > item.quantity:
                raise serializers.ValidationError({
                    'quantity_change': f'Cannot remove {abs(quantity_change)} items. Only {item.quantity} available.'
                })
            
            # Business rule: Require reason for adjustments
            if movement_type == 'ADJUST' and not data.get('reason'):
                raise serializers.ValidationError({
                    'reason': 'Reason is required for inventory adjustments'
                })
        
        return data


# ---------------------------------------------------------------------------- #
#                                   RESTOCK ALERT                                    #
# ---------------------------------------------------------------------------- #
class RestockAlertSerializer(serializers.ModelSerializer):
    item_detail = ItemSerializer(source='item', read_only=True)
    
    class Meta:
        model = models.RestockAlert
        fields = [
            'id', 'item', 'item_detail', 'predicted_days_until_zero',
            'current_quantity', 'avg_daily_consumption', 'is_resolved',
            'created_at', 'resolved_at'
        ]
        read_only_fields = [
            'predicted_days_until_zero', 'avg_daily_consumption', 
            'created_at'
        ]

    def validate(self, data):
        # When marking as resolved, set the resolved_at timestamp
        if 'is_resolved' in data and data['is_resolved']:
            data['resolved_at'] = timezone.now()
        return data


# ---------------------------------------------------------------------------- #
#                                     AUDIT LOG                                      #
# ---------------------------------------------------------------------------- #
class AuditLogSerializer(serializers.ModelSerializer):
    # Show user-friendly representations
    user = serializers.StringRelatedField(source='user_id')
    item_sku = serializers.CharField(source='item_id.sku', read_only=True)
    item_name = serializers.CharField(source='item_id.name', read_only=True)
    
    # Parse JSON fields
    old_values = serializers.JSONField()
    new_values = serializers.JSONField()
    
    class Meta:
        model = models.AuditLog
        fields = [
            'id', 'user', 'item_id', 'item_sku', 'item_name',
            'action_type', 'old_values', 'new_values',
            'ip_address', 'timestamp'
        ]
        read_only_fields = '__all__'  # Completely read-only


# ---------------------------------------------------------------------------- #
#                                   USER (AUTH)                                     #
# ---------------------------------------------------------------------------- #
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'first_name', 'last_name']
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True}
        }

    def create(self, validated_data):
        # Use create_user to hash password properly
        return User.objects.create_user(**validated_data)

    def validate_email(self, value):
        # Check if email already exists
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists")
        return value
