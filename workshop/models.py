from django.db import models

class Customer(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
class Technician(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class WorkOrder(models.Model):
    work_order_number = models.CharField(max_length=20, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    product_type = models.CharField(max_length=100)
    product_brand = models.CharField(max_length=100)
    product_model = models.CharField(max_length=100)
    serial_number = models.CharField(max_length=100, unique=True)
    issue_description = models.TextField()
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    estimated_completion_date = models.DateField(null=True, blank=True)
    is_repaired = models.BooleanField(null=True, blank=True)
    repair_details = models.TextField(null=True, blank=True)
    reason_for_not_repairing = models.TextField(null=True, blank=True)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    technician = models.ForeignKey(Technician, on_delete=models.SET_NULL, null=True)
    customer_collected = models.BooleanField(default=False)
    date_collected = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('ready_for_collection', 'Ready for Collection'),
        ('collected', 'Collected')
    ], default='pending')

    def __str__(self):
        return f"Work Order {self.id} - {self.status}"  

class ProductImage(models.Model):
    work_order = models.ForeignKey(WorkOrder, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="workorder_images/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.work_order.work_order_number}"
              

# Create your models here.
