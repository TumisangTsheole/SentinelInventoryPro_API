from rest_framework import generics, viewsets, permissions
from rest_framework.response import Response
from django.contrib.auth.models import User
from . import models, serializers

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = models.Category.objects.all()
    serializer_class = serializers.CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

class ItemViewSet(viewsets.ModelViewSet):
    queryset = models.Item.objects.all()
    serializer_class = serializers.ItemSerializer

    def perform_create(self, serializer):
        # Automatically set created_by and updated_by to the current user
        serializer.save(
            created_by=self.request.user,
            updated_by=self.request.user
        )

    def perform_update(self, serializer):
        # Only update the updated_by field (created_by stays as original)
        serializer.save(updated_by=self.request.user)

class StockMovementViewSet(viewsets.ModelViewSet):
    queryset = models.StockMovement.objects.all()
    serializer_class = serializers.StockMovementSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class RestockAlertViewSet(viewsets.ModelViewSet):
    queryset = models.RestockAlert.objects.all()
    serializer_class = serializers.RestockAlertSerializer

class AuditLogViewSet(viewsets.ModelViewSet):
    queryset = models.AuditLog.objects.all()
    serializer_class = serializers.AuditLogSerializer
    # Make it read-only
    http_method_names = ['get', 'head', 'options']  # No POST/PUT/DELETE

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = [permissions.AllowAny] # Anyone can register
    
    
