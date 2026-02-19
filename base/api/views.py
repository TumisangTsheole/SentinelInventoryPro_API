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

class StockMovementViewSet(viewsets.ModelViewSet):
    queryset = models.StockMovement.objects.all()
    serializer_class = serializers.StockMovementSerializer

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
    
    
