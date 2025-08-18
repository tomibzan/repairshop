from django.contrib import admin
from .models import Customer, Technician, WorkOrder, ProductImage

class ProductImageInline(admin.TabularInline):  # or StackedInline if you prefer big previews
    model = ProductImage
    extra = 1


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "email", "phone_number")
    search_fields = ("first_name", "last_name", "email", "phone_number")


@admin.register(Technician)
class TechnicianAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "email", "phone_number")
    search_fields = ("first_name", "last_name", "email", "phone_number")


@admin.register(WorkOrder)
class WorkOrderAdmin(admin.ModelAdmin):
    list_display = (
        "work_order_number",
        "customer",
        "technician",
        "status",
        "date_created",
        "date_updated",
    )
    search_fields = (
        "work_order_number",
        "serial_number",
        "customer__first_name",  # <-- allows searching by customer's first name
        "customer__last_name",
    )
    list_filter = ("status", "technician", "date_created", "customer_collected")
    ordering = ("-date_created",)
    inlines = [ProductImageInline]


