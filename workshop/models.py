from django.db import models

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
    work_order_number = models.CharField(max_length=20, unique=True, blank=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    technician = models.ForeignKey(Technician, on_delete=models.SET_NULL, null=True, blank=True)

    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    date_collected = models.DateTimeField(null=True, blank=True)

    product_type = models.CharField(max_length=100)
    product_brand = models.CharField(max_length=100)
    product_model = models.CharField(max_length=100)
    serial_number = models.CharField(max_length=100, unique=True)

    issue_description = models.TextField()
    repair_details = models.TextField(null=True, blank=True)
    reason_for_not_repairing = models.TextField(null=True, blank=True)

    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    estimated_completion_date = models.DateField(null=True, blank=True)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    is_repaired = models.BooleanField(null=True, blank=True)
    customer_collected = models.BooleanField(default=False)

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('ready_for_collection', 'Ready for Collection'),
        ('collected', 'Collected'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def save(self, *args, **kwargs):
        """Auto-generate work order number if missing."""
        if not self.work_order_number:
            last_wo = WorkOrder.objects.order_by("-id").first()
            if last_wo and last_wo.work_order_number.startswith("WO"):
                last_number = int(last_wo.work_order_number[2:])
            else:
                last_number = 1000
            new_number = last_number + 1
            if new_number > 9999:
                raise ValueError("Maximum work order number reached (9999)")
            self.work_order_number = f"WO{new_number}"
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
