from django.db import models
from django.contrib.auth.models import User
from rest_framework import generics, viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from . import models as local_models
from . import serializers
from .permissions import IsViewer, IsStocker, IsAdmin
from .filters import ItemFilter

# ---------------------------------------------------------------------------- #
#                                User Registration                             #
# ---------------------------------------------------------------------------- #
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = [permissions.AllowAny]


# ---------------------------------------------------------------------------- #
#                                   Category                                   #
# ---------------------------------------------------------------------------- #
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = local_models.Category.objects.all()
    serializer_class = serializers.CategorySerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated, IsViewer]
        elif self.action in ['create', 'update', 'partial_update']:
            permission_classes = [permissions.IsAuthenticated, IsStocker]
        elif self.action == 'destroy':
            permission_classes = [permissions.IsAuthenticated, IsAdmin]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]


# ---------------------------------------------------------------------------- #
#                                      Item                                    #
# ---------------------------------------------------------------------------- #
class ItemViewSet(viewsets.ModelViewSet):
    queryset = local_models.Item.objects.all()
    serializer_class = serializers.ItemSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ItemFilter
    search_fields = ['name', 'sku', 'description']
    ordering_fields = ['name', 'price', 'quantity', 'created_at']
    ordering = ['name']

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'low_stock', 'movements', 'prediction', 'predictions']:
            permission_classes = [permissions.IsAuthenticated, IsViewer]
        elif self.action in ['create', 'update', 'partial_update']:
            permission_classes = [permissions.IsAuthenticated, IsStocker]
        elif self.action == 'destroy':
            permission_classes = [permissions.IsAuthenticated, IsAdmin]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user,
            updated_by=self.request.user
        )

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    @action(detail=True, methods=['get'])
    def prediction(self, request, pk=None):
        """Get restock prediction for a single item."""
        item = self.get_object()
        serializer = serializers.ItemPredictionSerializer(item)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def predictions(self, request):
        """Get predictions for all items (optionally filter by needs_restock)."""
        items = self.get_queryset()
        needs_restock = request.query_params.get('needs_restock', '').lower()
        if needs_restock == 'true':
            filtered = []
            for item in items:
                days = item.predicted_days_until_zero()
                if days is not None and days <= 14:
                    filtered.append(item)
            items = filtered
        elif needs_restock == 'false':
            filtered = []
            for item in items:
                days = item.predicted_days_until_zero()
                if days is None or days > 14:
                    filtered.append(item)
            items = filtered

        serializer = serializers.ItemPredictionSerializer(items, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """Return all items where quantity <= reorder_threshold."""
        items = self.get_queryset().filter(quantity__lte=models.F('reorder_threshold'))
        serializer = self.get_serializer(items, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def movements(self, request, pk=None):
        """Return all stock movements for this item."""
        item = self.get_object()
        movements = item.stockmovement_set.all().order_by('-created_at')
        serializer = serializers.StockMovementSerializer(movements, many=True)
        return Response(serializer.data)


# ---------------------------------------------------------------------------- #
#                                Stock Movement                                #
# ---------------------------------------------------------------------------- #
class StockMovementViewSet(viewsets.ModelViewSet):
    queryset = local_models.StockMovement.objects.all()
    serializer_class = serializers.StockMovementSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated, IsViewer]
        elif self.action in ['create', 'update', 'partial_update']:
            permission_classes = [permissions.IsAuthenticated, IsStocker]
        elif self.action == 'destroy':
            permission_classes = [permissions.IsAuthenticated, IsAdmin]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# ---------------------------------------------------------------------------- #
#                                 Restock Alert                                #
# ---------------------------------------------------------------------------- #
class RestockAlertViewSet(viewsets.ModelViewSet):
    queryset = local_models.RestockAlert.objects.all()
    serializer_class = serializers.RestockAlertSerializer
    http_method_names = ['get', 'patch', 'head', 'options']  # no POST, PUT, DELETE

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated, IsViewer]
        elif self.action == 'partial_update':
            permission_classes = [permissions.IsAuthenticated, IsStocker]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    @classmethod
    def update_all(cls):
        """
        Class method to be called from a management command or cron job.
        Deletes unresolved alerts and creates new ones based on current predictions.
        """
        # Delete old unresolved alerts
        cls.objects.filter(is_resolved=False).delete()
        # For each item with prediction <= 14 days, create an alert
        for item in local_models.Item.objects.all():
            days = item.predicted_days_until_zero()
            if days is not None and days <= 14:
                cls.objects.create(
                    item=item,
                    predicted_days_until_zero=days,
                    current_quantity=item.quantity,
                    avg_daily_consumption=item.get_average_daily_consumption(),
                    is_resolved=False
                )


# ---------------------------------------------------------------------------- #
#                                   Audit Log                                  #
# ---------------------------------------------------------------------------- #
class AuditLogViewSet(viewsets.ModelViewSet):
    queryset = local_models.AuditLog.objects.all()
    serializer_class = serializers.AuditLogSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    http_method_names = ['get', 'head', 'options']  # read‑only
