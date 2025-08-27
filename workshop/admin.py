from django.contrib import admin
from .models import Customer, Technician, WorkOrder, ProductImage, RemoteRequest
from django.utils import timezone
from django.db import transaction

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

@admin.register(RemoteRequest)
class RemoteRequestAdmin(admin.ModelAdmin):
    list_display = ("customer_name", "customer_email", "customer_phone", "status", "created_at")
    list_filter = ("status", "preferred_tool", "created_at")
    search_fields = ("customer_name", "customer_email", "customer_phone", "connection_id", "issue_description")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("Customer Info", {
            "fields": ("customer_name", "customer_email", "customer_phone")
        }),
        ("Issue Details", {
            "fields": ("issue_description", "preferred_tool", "connection_id")
        }),
        ("Workflow", {
            "fields": ("status", "reviewed_by")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at")
        }),
    )    


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

class OverdueFilter(admin.SimpleListFilter):
    title = "Overdue Status"
    parameter_name = "overdue"

    def lookups(self, request, model_admin):
        return (("yes", "Overdue"), ("no", "On time"))

    def queryset(self, request, queryset):
        today = timezone.now().date()
        if self.value() == "yes":
            return queryset.filter(
                estimated_completion_date__lt=today,
                status__in=["pending", "in_progress"],
            )
        if self.value() == "no":
            return queryset.filter(
                estimated_completion_date__gte=today
            )
        return queryset

# ─────────────────────────────
# WorkOrder Admin (with images)
# ─────────────────────────────
@admin.register(WorkOrder)
class WorkOrderAdmin(admin.ModelAdmin):
    readonly_fields = ("work_order_number", "created_at", "updated_at")
    list_display = (
        "work_order_number", "customer", "status", "is_active",
        "technician", "product_type", "created_at", "updated_at"
    )
    list_filter = ("status", "created_at", "updated_at", "is_active", OverdueFilter)
    search_fields = ("work_order_number", "customer__first_name", "customer__last_name")
    actions = ["mark_as_completed", "mark_as_ready_for_pickup", "assign_to_technician"]
    ordering = ("-created_at",)
    inlines = [ProductImageInline]

    def mark_as_completed(self, request, queryset):
        updated = queryset.update(status="completed")
        self.message_user(request, f"{updated} work orders marked as Completed.")
    mark_as_completed.short_description = "Mark selected orders as Completed"

    def mark_as_ready_for_pickup(self, request, queryset):
        updated = queryset.update(status="ready_for_pickup")
        self.message_user(request, f"{updated} work orders marked as Ready for Pickup.")
    mark_as_ready_for_pickup.short_description = "Mark selected orders as Ready for Pickup"

    def assign_to_technician(self, request, queryset):
        # For now, just assign to the first technician (later we add a form for choosing)
        tech = Technician.objects.first()
        updated = queryset.update(technician=tech)
        self.message_user(request, f"{updated} work orders assigned to {tech}.")
    assign_to_technician.short_description = "Assign selected orders to first available Technician"

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
