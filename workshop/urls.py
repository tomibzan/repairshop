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
    path("bulk-update/", views.landing_bulk_update, name="landing_bulk_update"),
    path("search/", views.search, name="search"),
    path("workorders/", views.workorder_list, name="workorder_list"),
    path("workorder/<int:pk>/", views.workorder_detail, name="workorder_detail"),
    path("api/", include(router.urls)),
    path("remote-request/", views.remote_request_submit, name="remote_request"),
    path("remote-requests/", views.remote_request_list, name="remote_request_list"),
    path("remote-request/", views.remote_request_create, name="remote_request_create"),
    path("remote-request/thank-you/", views.remote_request_thankyou, name="remote_request_thankyou"),
    path("remote-request/<int:pk>/convert/", views.convert_remote_request, name="convert_remote_request"),
    path("remote-request/", views.remote_service_request, name="remote_service_request"),
]
