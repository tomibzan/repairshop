from django.db import models
from django.utils import timezone

# ─────────────────────────────
# Customer
# ─────────────────────────────
class Customer(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


# ─────────────────────────────
# Technician
# ─────────────────────────────
class Technician(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


# ─────────────────────────────
# Work Order
# ─────────────────────────────
class WorkOrder(models.Model):
    customer = models.ForeignKey("Customer", on_delete=models.CASCADE)
    product_type = models.CharField(max_length=100)
    product_brand = models.CharField(max_length=100)
    product_model = models.CharField(max_length=100)
    serial_number = models.CharField(max_length=100, blank=True, null=True)
    issue_description = models.TextField()
    product_image = models.ImageField(upload_to="workorder_images/", blank=True, null=True)
    work_order_number = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    technician = models.ForeignKey("Technician", on_delete=models.SET_NULL, null=True, blank=True)
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    estimated_completion_date = models.DateField(blank=True, null=True)
    reason_for_not_repairing = models.TextField(null=True, blank=True)
    date_collected = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=50,
        choices=[
            ("pending", "Pending"),
            ("in_progress", "In Progress"),
            ("completed", "Completed"),
            ("cancelled", "Cancelled"),
        ],
        default="pending"
    )

    is_repaired = models.BooleanField(default=False)
    repair_details = models.TextField(blank=True, null=True)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    not_repaired_reason = models.TextField(blank=True, null=True)
    customer_collected = models.BooleanField(default=False)
    collected_at = models.DateTimeField(blank=True, null=True)

    def save(self, *args, **kwargs):
        # Auto-generate work order number only once
        if not self.work_order_number:
            year = timezone.now().year
            last_order = WorkOrder.objects.filter(
                created_at__year=year
            ).order_by("id").last()
            
            if last_order and last_order.work_order_number:
                last_number = int(last_order.work_order_number.split("-")[-1])
                new_number = last_number + 1
            else:
                new_number = 1

            self.work_order_number = f"WO-{year}-{new_number:04d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.work_order_number} - {self.customer}"


# ─────────────────────────────
# Product Image
# ─────────────────────────────
class ProductImage(models.Model):
    work_order = models.ForeignKey(
        WorkOrder,
        on_delete=models.CASCADE,
        related_name="images"
    )
    image = models.ImageField(upload_to="workorder_images/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.work_order.work_order_number} ({self.id})"
