from django.contrib import admin
from .models import Customer, Technician, WorkOrder, ProductImage

# ─────────────────────────────
# Inline: Product Images
# ─────────────────────────────
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ("image", "uploaded_at")
    readonly_fields = ("uploaded_at",)


# ─────────────────────────────
# Customer Admin
# ─────────────────────────────
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "email", "phone_number")
    search_fields = ("first_name", "last_name", "email", "phone_number")
    ordering = ("first_name",)


# ─────────────────────────────
# Technician Admin
# ─────────────────────────────
@admin.register(Technician)
class TechnicianAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "email", "phone_number")
    search_fields = ("first_name", "last_name", "email", "phone_number")
    ordering = ("first_name",)


# ─────────────────────────────
# WorkOrder Admin (with images)
# ─────────────────────────────
@admin.register(WorkOrder)
class WorkOrderAdmin(admin.ModelAdmin):
    readonly_fields = ("work_order_number", "date_created", "date_updated")
    list_display = (
        "work_order_number",
        "customer",
        "technician",
        "status",
        "date_created",
        "estimated_cost",
        "total_cost",
        "customer_collected",
    )
    search_fields = (
        "work_order_number",
        "serial_number",
        "product_type",
        "product_brand",
        "product_model",
        "customer__first_name",
        "customer__last_name",
        "technician__first_name",
        "technician__last_name",
    )
    list_filter = ("status", "date_created", "date_updated", "customer_collected", "is_repaired")
    ordering = ("-date_created",)
    inlines = [ProductImageInline]
