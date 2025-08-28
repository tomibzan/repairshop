from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.urls import reverse
from .models import Customer, Technician, WorkOrder, ProductImage, RemoteRequest
from django.utils import timezone
from django.db import transaction
from django.utils.html import format_html
from django.contrib.admin import AdminSite



class CustomAdminSite(AdminSite):
    site_header = "Ethiofolks Repair Shop Admin"
    site_title = "Repair Shop Admin Portal" 
    index_title = "Welcome to the Repair Shop Dashboard"

custom_admin_site = CustomAdminSite(name='custom_admin')

def send_status_email_action(self, request, queryset):
    """Admin action to manually send status emails"""
    from .utils import send_status_update_email
    
    sent_count = 0
    for workorder in queryset:
        if send_status_update_email(workorder):
            sent_count += 1
    
    self.message_user(request, f"Status emails sent to {sent_count} customers.")
send_status_email_action.short_description = "Send status email to selected customers"

# Add to your actions list
actions = ["mark_as_completed", "mark_as_ready_for_pickup", "assign_to_technician", "send_status_email_action"]

def get_app_list(self, request, app_label=None):
        """
        Return a sorted list of all the installed apps that have been
        registered in this site.
        """
        app_dict = self._build_app_dict(request)
        
        # Sort the apps alphabetically
        app_list = sorted(app_dict.values(), key=lambda x: x['name'].lower())
        
        # Custom ordering for workshop app models
        for app in app_list:
            if app['app_label'] == 'workshop':
                # Define your desired order
                desired_order = ['workorder', 'remoterequest', 'customer', 'technician']
                
                # Create a mapping for sorting
                order_mapping = {model: index for index, model in enumerate(desired_order)}
                
                # Sort the models based on desired order
                app['models'].sort(key=lambda x: order_mapping.get(x['object_name'].lower(), 999))
        
        return super().get_app_list(request, app_label)



# ─────────────────────────────
# REGISTER AUTH MODELS WITH CUSTOM ADMIN SITE
# ─────────────────────────────
@admin.register(User, site=custom_admin_site)
class CustomUserAdmin(UserAdmin):
    pass

@admin.register(Group, site=custom_admin_site)
class CustomGroupAdmin(GroupAdmin):
    pass

# ─────────────────────────────
# Inline: Product Images
# ─────────────────────────────
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ("image", "uploaded_at")
    readonly_fields = ("uploaded_at",)

# ─────────────────────────────
# RemoteRequest Admin
# ─────────────────────────────
@admin.register(RemoteRequest, site=custom_admin_site)
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
@admin.register(Customer, site=custom_admin_site)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "email", "phone_number")
    search_fields = ("first_name", "last_name", "email", "phone_number")
    ordering = ("first_name",)

# ─────────────────────────────
# Technician Admin
# ─────────────────────────────
@admin.register(Technician, site=custom_admin_site)
class TechnicianAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "email", "phone_number")
    search_fields = ("first_name", "last_name", "email", "phone_number")
    ordering = ("first_name",)

# ─────────────────────────────
# Overdue Filter
# ─────────────────────────────
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
# WorkOrder Admin
# ─────────────────────────────
@admin.register(WorkOrder, site=custom_admin_site)
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
        if obj:
            fields = ["work_order_number", "created_at", "updated_at"] + fields
        return fields