from rest_framework import generics, viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth.models import User
from . import models, serializers
from .permissions import IsViewer, IsStocker, IsAdmin
from .serializers import ItemPredictionSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = models.Category.objects.all()
    serializer_class = serializers.CategorySerializer
    permission_classes = [permissions.IsAuthenticated, IsStocker]

    def get_permissions(self):
        """
        Customize permissions per action.
        """
        if self.action in ['list', 'retrieve']:
            # Allow Viewers to read
            return [IsAuthenticated(), IsViewer()]
        elif self.action in ['create', 'update', 'partial_update']:
            # Allow Stockers and above to write
            return [IsAuthenticated(), IsStocker()]
        elif self.action == 'destroy':
            # Only Admins can delete
            return [IsAuthenticated(), IsAdmin()]
        return super().get_permissions()

class ItemViewSet(viewsets.ModelViewSet):
    queryset = models.Item.objects.all()
    serializer_class = serializers.ItemSerializer
    permission_classes = [permissions.IsAuthenticated, IsStocker]

    def perform_create(self, serializer):
        # Automatically set created_by and updated_by to the current user
        serializer.save(
            created_by=self.request.user,
            updated_by=self.request.user
        )
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated(), IsViewer()]
        elif self.action in ['create', 'update', 'partial_update']:
            return [IsAuthenticated(), IsStocker()]
        elif self.action == 'destroy':
            return [IsAuthenticated(), IsAdmin()]
        return super().get_permissions()

    def perform_update(self, serializer):
        # Only update the updated_by field (created_by stays as original)
        serializer.save(updated_by=self.request.user)

    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated, IsViewer])
    def prediction(self, request, pk=None):
        """Get restock prediction for a single item."""
        item = self.get_object()
        serializer = ItemPredictionSerializer(item)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated, IsViewer])
    def predictions(self, request):
        """Get predictions for all items (optionally filter by needs_restock)."""
        items = self.get_queryset()
        # Optional query param to filter only items needing restock
        needs_restock = request.query_params.get('needs_restock', '').lower()
        if needs_restock == 'true':
            # We have to filter in Python because it's a computed property
            # For large datasets, you'd want a more efficient approach (e.g., annotate in DB)
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

        serializer = ItemPredictionSerializer(items, many=True)
        return Response(serializer.data)            

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated, IsViewer])
        def low_stock(self, request):
            """Return all items where quantity <= reorder_threshold."""
            items = self.get_queryset().filter(quantity__lte=models.F('reorder_threshold'))
            serializer = self.get_serializer(items, many=True)
            return Response(serializer.data)

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated, IsViewer])
        def movements(self, request, pk=None):
            """Return all stock movements for this item."""
            item = self.get_object()
            movements = item.stockmovement_set.all().order_by('-created_at')
            serializer = StockMovementSerializer(movements, many=True)
            return Response(serializer.data)            
            

class StockMovementViewSet(viewsets.ModelViewSet):
    queryset = models.StockMovement.objects.all()
    serializer_class = serializers.StockMovementSerializer
    permission_classes = [permissions.IsAuthenticated, IsStocker]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated(), IsViewer()]
        elif self.action in ['create', 'update', 'partial_update']:
            return [IsAuthenticated(), IsStocker()]
        elif self.action == 'destroy':
            # maybe only admins can delete movements?
            return [IsAuthenticated(), IsAdmin()]
        return super().get_permissions()    

class RestockAlertViewSet(viewsets.ModelViewSet):
    queryset = models.RestockAlert.objects.all()
    serializer_class = serializers.RestockAlertSerializer
    permission_classes = [permissions.IsAuthenticated, IsStocker]
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated(), IsViewer()]
        elif self.action == 'partial_update':
            # Allow stockers to resolve alerts (patch is_resolved)
            return [IsAuthenticated(), IsStocker()]
        # No create/delete for alerts
        return super().get_permissions()

    @classmethod
    def update_all(cls):
        # Delete old unresolved alerts
        cls.objects.filter(is_resolved=False).delete()
        # For each item with prediction <= 14 days, create an alert
        for item in Item.objects.all():
            days = item.predicted_days_until_zero()
            if days is not None and days <= 14:
                cls.objects.create(
                    item=item,
                    predicted_days_until_zero=days,
                    current_quantity=item.quantity,
                    avg_daily_consumption=item.get_average_daily_consumption(),
                    is_resolved=False
                )    

class AuditLogViewSet(viewsets.ModelViewSet):
    queryset = models.AuditLog.objects.all()
    serializer_class = serializers.AuditLogSerializer
    # Make it read-only
    http_method_names = ['get', 'head', 'options']  # No POST/PUT/DELETE

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = [permissions.AllowAny] # Anyone can register
    
    
