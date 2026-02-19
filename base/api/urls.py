from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views


router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet)
router.register(r'items', views.ItemViewSet)
router.register(r'stock-movements', views.StockMovementViewSet)
router.register(r'restock-alerts', views.RestockAlertViewSet)
router.register(r'audit-logs', views.AuditLogViewSet)


urlpatterns = [
    path('', include(router.urls)),

    path('auth/register/', views.RegisterView.as_view(), name='register')
]
