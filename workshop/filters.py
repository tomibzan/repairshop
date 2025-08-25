import django_filters
from .models import WorkOrder

class WorkOrderFilter(django_filters.FilterSet):
    date_created_after = django_filters.DateFilter(field_name="date_created", lookup_expr="gte")
    date_created_before = django_filters.DateFilter(field_name="date_created", lookup_expr="lte")
    status = django_filters.CharFilter(field_name="status")
    technician_id = django_filters.NumberFilter(field_name="technician__id")
    customer_id = django_filters.NumberFilter(field_name="customer__id")
    is_repaired = django_filters.BooleanFilter(field_name="is_repaired")

    class Meta:
        model = WorkOrder
        fields = [
            "status",
            "technician_id",
            "customer_id",
            "is_repaired",
            "date_created_after",
            "date_created_before",
        ]
