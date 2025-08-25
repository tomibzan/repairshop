from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router
router = DefaultRouter()
router.register(r'customers', views.CustomerViewSet, basename="customer")
router.register(r'workorders', views.WorkOrderViewSet, basename="workorder")
router.register(r'images', views.ProductImageViewSet, basename="workorderimage")

urlpatterns = [
    path("", include(router.urls)),  # browsable API homepage at /api/
]
