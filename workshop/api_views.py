from rest_framework import viewsets, filters
from django.db.models import Count, Sum
from .models import WorkOrder, Customer, ProductImage
from .serializers import WorkOrderSerializer, CustomerSerializer, ProductImageSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils.dateparse import parse_date
from django.http import JsonResponse


class WorkOrderViewSet(viewsets.ModelViewSet):
    queryset = WorkOrder.objects.all()
    serializer_class = WorkOrderSerializer
    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ["product_model", "status", "notes"]
    ordering_fields = ["date_created", "total_cost", "status"]  # allowed order fields
    ordering = ["-date_created"]  # default: newest first

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

    # Optional: search + ordering
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "phone", "email"]
    ordering_fields = ["name", "created_at"]  #  

class ProductImageViewSet(viewsets.ModelViewSet):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["uploaded_at"]



@api_view(["GET"])
def dashboard_summary(request):
    # Parse optional date range from query params
    start_date = parse_date(request.GET.get("start_date"))
    end_date = parse_date(request.GET.get("end_date"))

    workorders = WorkOrder.objects.all()
    if start_date and end_date:
        workorders = workorders.filter(created_at__date__range=[start_date, end_date])

    total_customers = Customer.objects.count()
    total_orders = workorders.count()
    pending_orders = workorders.filter(status="pending").count()
    completed_orders = workorders.filter(status="completed").count()
    total_revenue = workorders.aggregate(Sum("total_cost"))["total_cost__sum"] or 0

    # cost per customer (within filtered range if applied)
    cost_per_customer = (
        workorders.values("customer__first_name", "customer__last_name")
        .annotate(total_orders=Count("id"))
        .order_by()
    )

    return Response({
        "total_customers": total_customers,
        "total_orders": total_orders,
        "pending_orders": pending_orders,
        "completed_orders": completed_orders,
        "total_revenue": total_revenue,
        "cost_per_customer": list(cost_per_customer),
    })