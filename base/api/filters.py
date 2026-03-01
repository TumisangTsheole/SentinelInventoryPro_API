import django_filters
from .models import Item

class ItemFilter(django_filters.FilterSet):
    # Low stock filter: quantity <= reorder_threshold
    low_stock = django_filters.BooleanFilter(method='filter_low_stock', label='Low stock')

    class Meta:
        model = Item
        fields = {
            'category': ['exact'],
            'is_active': ['exact'],
            'price': ['lt', 'gt', 'exact'],
            'quantity': ['lt', 'gt', 'exact'],
        }

    def filter_low_stock(self, queryset, name, value):
        if value:
            return queryset.filter(quantity__lte=models.F('reorder_threshold'))
        return queryset
