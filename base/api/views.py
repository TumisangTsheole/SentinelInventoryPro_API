from rest_framework import generics, viewsets, permissions
from rest_framework.response import Response
from django.contrib.auth.models import User
from . import models, serializers
from .permissions import IsViewer, IsStocker, IsAdmin

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

class AuditLogViewSet(viewsets.ModelViewSet):
    queryset = models.AuditLog.objects.all()
    serializer_class = serializers.AuditLogSerializer
    # Make it read-only
    http_method_names = ['get', 'head', 'options']  # No POST/PUT/DELETE

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = [permissions.AllowAny] # Anyone can register
    
    
