from django.contrib import admin
from .models import Customer, Technician, WorkOrder, ProductImage

admin.site.site_header = "Ethiofolks Repair Shop Admin"   # The top bar header
admin.site.site_title = "Repair Shop Admin Portal"        # The browser tab title
admin.site.index_title = "Welcome to the Repair Shop Dashboard"  # Main index page text

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
    readonly_fields = ("work_order_number", "created_at", "updated_at")
    list_display = (
        "work_order_number", "customer", "status",
        "technician", "product_type", "created_at", "updated_at"
    )
    list_filter = ("status", "created_at", "updated_at")
    search_fields = ("work_order_number", "customer__first_name", "customer__last_name")
    ordering = ("-created_at",)
    inlines = [ProductImageInline]

    def get_fields(self, request, obj=None):
        fields = [
            "customer",
            "product_type",
            "product_brand",
            "product_model",
            "serial_number",
            "issue_description",
            "technician",
            "estimated_cost",
            "estimated_completion_date",
            "status",
            "is_repaired",
            "repair_details",
            "total_cost",
            "reason_for_not_repairing",
            "customer_collected",
            "date_collected",
        ]
        if obj:  # If editing an existing object, include read-only fields
            fields = ["work_order_number", "created_at", "updated_at"] + fields
        return fields 
