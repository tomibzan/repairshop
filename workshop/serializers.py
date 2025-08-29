from rest_framework import serializers
from .models import Customer, Technician, WorkOrder, ProductImage

# ─────────────────────────────
# Customer Serializer
# ─────────────────────────────
class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ["id", "first_name", "last_name", "email", "phone_number"]

# ─────────────────────────────
# Technician Serializer
# ─────────────────────────────
class TechnicianSerializer(serializers.ModelSerializer):
    class Meta:
        model = Technician
        fields = ["id", "first_name", "last_name", "email", "phone_number"]

# ─────────────────────────────
# ProductImage Serializer
# ─────────────────────────────
class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id", "work_order", "image", "uploaded_at"]
        read_only_fields = ["uploaded_at"]

# ─────────────────────────────
# WorkOrder Serializer
# ─────────────────────────────
class WorkOrderSerializer(serializers.ModelSerializer):
    # Nested serializers for better API responses
    customer = CustomerSerializer(read_only=True)
    technician = TechnicianSerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)

    # Accept IDs when creating/updating
    customer_id = serializers.PrimaryKeyRelatedField(
        queryset=Customer.objects.all(), source="customer", write_only=True
    )
    technician_id = serializers.PrimaryKeyRelatedField(
        queryset=Technician.objects.all(), source="technician", write_only=True, required=False
    )

    class Meta:
        model = WorkOrder
        fields = [
            "id",
            "work_order_number",
            "customer",
            "customer_id",
            "technician",
            "technician_id",
            "product_type",
            "product_brand",
            "product_model",
            "serial_number",
            "issue_description",
            "estimated_cost",
            "estimated_completion_date",
            "is_repaired",
            "repair_details",
            "reason_for_not_repairing",
            "total_cost",
            "status",
            "customer_collected",
            "created_at",
            "updated_at",
            "date_collected",
            "images",
        ]
        read_only_fields = ["work_order_number", "created_at", "updated_at"]
