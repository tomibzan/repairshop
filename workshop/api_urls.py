from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views  # Only import API views here

# Create a router
router = DefaultRouter()
router.register("customers", api_views.CustomerViewSet, basename="customer")
router.register("workorders", api_views.WorkOrderViewSet, basename="workorder")
router.register("images", api_views.ProductImageViewSet, basename="workorderimage")

urlpatterns = [
    path("", include(router.urls)),  # browsable API homepage at /api/
    path("dashboard-summary/", api_views.dashboard_summary, name="dashboard-summary"),
]
