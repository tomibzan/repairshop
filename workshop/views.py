import re
from django.shortcuts import render
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Customer, Technician, WorkOrder, ProductImage
from .serializers import (
    CustomerSerializer,
    TechnicianSerializer,
    WorkOrderSerializer,
    ProductImageSerializer,
)
from django_filters.rest_framework import DjangoFilterBackend
from .filters import WorkOrderFilter
from django.db.models import Q


def normalize_phone(phone: str) -> str:
    """Normalize Ethiopian phone numbers for search consistency."""
    if not phone:
        return ""
    digits = re.sub(r"\D", "", phone)

    # Handle common Ethiopian formats
    if digits.startswith("0"):             # e.g. 0912...
        return "+251" + digits[1:]
    elif digits.startswith("251"):         # e.g. 251912...
        return "+" + digits
    elif digits.startswith("9") and len(digits) == 9:  # e.g. 912...
        return "+251" + digits
    return phone  # fallback (maybe already in +251...)


def landing(request):
    q = request.GET.get("q", "").strip()
    results = []
    searched = False

    if q:
        searched = True

        normalized_phone = normalize_phone(q)

        qs = (
            WorkOrder.objects
            .select_related("customer", "technician")
            .order_by("-created_at" if hasattr(WorkOrder, "created_at") else "-id")
        )

        filters = Q(customer__email__iexact=q)
        if normalized_phone:
            filters |= Q(customer__phone_number__icontains=normalized_phone)

        results = qs.filter(filters)

    return render(
        request,
        "workshop/landing.html",  # <-- use namespaced path
        {
            "query": q,
            "searched": searched,
            "results": results,
        },
    )
def search(request):
    query = request.GET.get("q", "")
    workorders = []
    if query:
        workorders = WorkOrder.objects.filter(id__iexact=query) | \
                     WorkOrder.objects.filter(customer__phone_number__icontains=query) | \
                     WorkOrder.objects.filter(customer__email__icontains=query)
    return render(request, "workshop/search.html", {"workorders": workorders, "query": query})

def workorder_detail(request, pk):
    workorder = get_object_or_404(WorkOrder, pk=pk)
    return render(request, "workshop/workorder_detail.html", {"workorder": workorder})



# ─────────────────────────────
# Customer ViewSet
# ─────────────────────────────
class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["first_name", "last_name", "email", "phone_number"]
    ordering_fields = ["first_name", "last_name"]


# ─────────────────────────────
# Technician ViewSet
# ─────────────────────────────
class TechnicianViewSet(viewsets.ModelViewSet):
    queryset = Technician.objects.all()
    serializer_class = TechnicianSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["first_name", "last_name", "email", "phone_number"]
    ordering_fields = ["first_name", "last_name"]


# ─────────────────────────────
# WorkOrder ViewSet
# ─────────────────────────────
class WorkOrderViewSet(viewsets.ModelViewSet):
    queryset = WorkOrder.objects.all().select_related("customer", "technician")
    serializer_class = WorkOrderSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    filterset_class = WorkOrderFilter
    search_fields = [
        "work_order_number",
        "customer__first_name",
        "customer__last_name",
        "technician__first_name",
        "technician__last_name",
        "product_type",
        "product_brand",
        "serial_number",
    ]
    ordering_fields = ["date_created", "status", "product_brand"]

    @action(detail=True, methods=["post"])
    def mark_repaired(self, request, pk=None):
        """Custom action to mark a work order as repaired"""
        work_order = self.get_object()
        work_order.is_repaired = True
        work_order.status = "completed"
        work_order.save()
        return Response({"status": "Work order marked as repaired"})


# ─────────────────────────────
# ProductImage ViewSet
# ─────────────────────────────
class ProductImageViewSet(viewsets.ModelViewSet):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["uploaded_at"]


# Create your views here.
