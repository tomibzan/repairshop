from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomerViewSet, TechnicianViewSet, WorkOrderViewSet, ProductImageViewSet
from . import views

app_name = "workshop"

router = DefaultRouter()
router.register(r"customers", CustomerViewSet)
router.register(r"technicians", TechnicianViewSet)
router.register(r"workorders", WorkOrderViewSet)
router.register(r"images", ProductImageViewSet)

urlpatterns = [
    path("", views.landing, name="landing"),
    path("search/", views.search, name="search"),
    path("workorder/<int:pk>/", views.workorder_detail, name="workorder_detail"),
    path("api/", include(router.urls)),
]
