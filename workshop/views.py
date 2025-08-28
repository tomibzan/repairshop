import re
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.utils.dateparse import parse_date
from django.core.paginator import Paginator
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required, permission_required
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .forms import RemoteRequestForm
from .models import Customer, RemoteRequest, Technician, WorkOrder, ProductImage
from .serializers import (
    CustomerSerializer,
    TechnicianSerializer,
    WorkOrderSerializer,
    ProductImageSerializer,
)
from django_filters.rest_framework import DjangoFilterBackend
from .filters import WorkOrderFilter
from django.urls import reverse
from django.db import transaction
from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from .utils import send_sms


def remote_service_request(request):
    success_message = None
    if request.method == "POST":
        form = RemoteRequestForm(request.POST)
        if form.is_valid():
            form.save()
            success_message = "Thank you! Your remote service request has been submitted successfully."
            form = RemoteRequestForm() 
    else:
        form = RemoteRequestForm()
    return render(request, "workshop/remote_request.html", {"form": form, "success_message": success_message})

def remote_request_submit(request):
    if request.method == "POST":
        form = RemoteRequestForm(request.POST)
        if form.is_valid():
            remote_request = form.save()

            # Shared context for both emails/SMS
            context = {
                "request": remote_request,
                "customer_name": remote_request.customer_name,
                "customer_contact": remote_request.customer_email or remote_request.customer_phone,
                "issue_description": remote_request.issue_description,
            }

            # --- Customer Email ---
            if remote_request.customer_email:
                customer_subject = "We Received Your Remote Service Request"
                customer_html = render_to_string(
                    "workshop/email/remote_request_customer.html", context
                )
                customer_msg = EmailMultiAlternatives(
                    customer_subject,
                    "Plain text fallback for clients that don’t render HTML.",
                    settings.DEFAULT_FROM_EMAIL,
                    [remote_request.customer_email],
                )
                customer_msg.attach_alternative(customer_html, "text/html")
                customer_msg.send()
            elif remote_request.customer_phone:
                # SMS fallback if email is not provided
                sms_message = (
                    f"Hi {remote_request.customer_name}, "
                    f"we received your service request. Issue: "
                    f"{remote_request.issue_description[:100]}..."
                )
                send_sms(remote_request.customer_phone, sms_message)

            # --- Admin Email ---
            admin_subject = f"New Remote Service Request from {remote_request.customer_name}"
            admin_html = render_to_string(
                "workshop/email/remote_request_admin.html", context
            )
            admin_msg = EmailMultiAlternatives(
                admin_subject,
                "New request submitted.",
                settings.DEFAULT_FROM_EMAIL,
                ["yourgmail@gmail.com"],  # TODO: replace with actual admin/staff email
            )
            admin_msg.attach_alternative(admin_html, "text/html")
            admin_msg.send()

            # Feedback to user
            messages.success(
                request,
                "Your remote service request has been submitted successfully! "
                "Our team will review it and contact you."
            )
            return redirect("workshop:remote_request")
    else:
        form = RemoteRequestForm()

    return render(request, "workshop/remote_request.html", {"form": form})

def remote_request_create(request):
    """Client submits a new remote service request"""
    if request.method == "POST":
        form = RemoteRequestForm(request.POST)
        if form.is_valid():
            remote_request = form.save()
            messages.success(
                request, 
                f"Thank you {remote_request.name}! Your remote service request has been received."
            )
            return redirect("workshop:remote_request_thankyou")
    else:
        form = RemoteRequestForm()
    return render(request, "workshop/remote_request_form.html", {"form": form})

def remote_request_thankyou(request):
    """Simple thank-you page after submission"""
    return render(request, "workshop/remote_request_thankyou.html")



@login_required
@permission_required("workshop.change_remoterequest", raise_exception=True)
def remote_request_list(request):
    requests = RemoteRequest.objects.all().order_by("-created_at")
    return render(request, "workshop/remote_request_list.html", {"requests": requests})


@login_required
@permission_required("workshop.change_remoterequest", raise_exception=True)
def convert_remote_request(request, pk):
    remote_req = get_object_or_404(RemoteRequest, pk=pk)

    # Create or get customer
    customer, _ = Customer.objects.get_or_create(
        email=remote_req.email,
        defaults={
            "first_name": remote_req.customer_name.split(" ")[0],
            "last_name": " ".join(remote_req.customer_name.split(" ")[1:]) or "",
            "phone": remote_req.phone,
        },
    )

    # Create WorkOrder
    workorder = WorkOrder.objects.create(
        customer=customer,
        product_type="Remote Service",
        repair_details=remote_req.issue_description,
        status="new",
    )

    remote_req.status = "converted"
    remote_req.save()

    messages.success(request, f"Remote request converted to Work Order #{workorder.work_order_number}")
    return redirect("workshop:remote_request_list")
# ─────────────────────────────
# Utility
# ─────────────────────────────
def normalize_phone(phone: str) -> str:
    if not phone:
        return ""
    digits = re.sub(r"\D", "", phone)
    if digits.startswith("0"):
        return "+251" + digits[1:]
    elif digits.startswith("251"):
        return "+" + digits
    elif digits.startswith("9") and len(digits) == 9:
        return "+251" + digits
    return phone


# ─────────────────────────────
# Landing Page / Customer Search
# ─────────────────────────────
def landing(request):
    q = request.GET.get("q", "").strip()
    results = []
    searched = False

    form = RemoteRequestForm(request.POST or None)

    if form.is_bound and form.is_valid():
        form.save()
        messages.success(request, "Your remote service request has been submitted!")
        return redirect('workshop:landing')

    if q:
        searched = True
        normalized_phone = normalize_phone(q)

        qs = WorkOrder.objects.select_related("customer", "technician").order_by("-created_at")

        # Build phone variants
        phone_variants = [q]
        if normalized_phone:
            phone_variants.append(normalized_phone)
        if q.startswith("+251") and len(q) == 13:
            phone_variants.append("0" + q[4:])

        phone_filter = Q()
        for p in phone_variants:
            phone_filter |= Q(customer__phone_number__icontains=p)

        filters_combined = Q(customer__email__icontains=q) | phone_filter
        results = qs.filter(filters_combined)

    return render(
        request,
        "workshop/landing.html",
        {
            "query": q,
            "searched": searched,
            "results": results,
            "form": form,
        },
    )


# ─────────────────────────────
# Bulk Update for Staff
# ─────────────────────────────
@staff_member_required
@require_POST
def landing_bulk_update(request):
    """
    Staff-only endpoint to perform bulk actions on selected work orders.
    Accepts checkbox inputs named either "workorder_ids" or "workorder_ids[]".
    Allowed actions: mark_completed, mark_ready, archive, assign_technician (with technician_id).
    """

    # Resolve redirect target (referer or landing page)
    referer = request.META.get("HTTP_REFERER")
    fallback = reverse("workshop:landing")
    redirect_to = referer or fallback

    # Try both possible checkbox naming conventions
    workorder_ids = request.POST.getlist("workorder_ids[]")
    if not workorder_ids:
        workorder_ids = request.POST.getlist("workorder_ids")

    action = request.POST.get("bulk_action")

    # Basic validation
    if not workorder_ids:
        messages.warning(request, "No work orders selected.")
        return redirect(redirect_to)

    # Extra permission check: user must be allowed to change workorders
    if not request.user.has_perm("workshop.change_workorder"):
        messages.error(request, "You do not have permission to perform bulk updates.")
        return redirect(redirect_to)

    # Sanitize and convert IDs to ints
    try:
        ids = [int(i) for i in workorder_ids if str(i).strip()]
    except ValueError:
        messages.error(request, "Invalid work order ID provided.")
        return redirect(redirect_to)

    qs = WorkOrder.objects.filter(id__in=ids, is_active=True)
    if not qs.exists():
        messages.warning(request, "No matching active work orders found.")
        return redirect(redirect_to)

    # Execute the requested action inside a transaction
    try:
        with transaction.atomic():
            if action == "mark_completed":
                updated = qs.update(status="completed")
                messages.success(request, f"{updated} work order(s) marked as Completed.")
            elif action == "mark_ready":
                updated = qs.update(status="ready_for_pickup")
                messages.success(request, f"{updated} work order(s) marked as Ready for Pickup.")
            elif action == "archive":
                updated = qs.update(is_active=False)
                messages.success(request, f"{updated} work order(s) archived.")
            elif action == "assign_technician":
                # expects a technician_id in POST
                tech_id = request.POST.get("technician_id")
                if not tech_id:
                    messages.error(request, "No technician selected for assignment.")
                    return redirect(redirect_to)
                # Optionally validate Technician exists:
                try:
                    tech_id_int = int(tech_id)
                except ValueError:
                    messages.error(request, "Invalid technician id.")
                    return redirect(redirect_to)
                updated = qs.update(technician_id=tech_id_int)
                messages.success(request, f"{updated} work order(s) assigned to technician (id: {tech_id_int}).")
            else:
                messages.error(request, "Invalid bulk action.")
                return redirect(redirect_to)
    except Exception as exc:
        # Catch unexpected DB errors and show user-friendly message
        messages.error(request, f"Failed to apply bulk action: {str(exc)}")
        return redirect(redirect_to)

    return redirect(redirect_to)
# ─────────────────────────────
# Standalone Search View (optional / separate page)
# ─────────────────────────────
def search(request):
    query = request.GET.get("q", "").strip()
    workorders = WorkOrder.objects.none()
    if query:
        workorders = (
            WorkOrder.objects.filter(id__iexact=query)
            | WorkOrder.objects.filter(customer__phone_number__icontains=query)
            | WorkOrder.objects.filter(customer__email__icontains=query)
        )
    return render(request, "workshop/search.html", {"workorders": workorders, "query": query})


# ─────────────────────────────
# WorkOrder Detail
# ─────────────────────────────
def workorder_detail(request, pk):
    workorder = get_object_or_404(WorkOrder, pk=pk)
    return render(request, "workshop/workorder_detail.html", {"workorder": workorder})


# ─────────────────────────────
# WorkOrder List (with filters / pagination)
# ─────────────────────────────
def workorder_list(request):
    qs = WorkOrder.objects.select_related("customer", "technician").all()

    q = request.GET.get("q")
    status = request.GET.get("status")
    customer = request.GET.get("customer")
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    if q:
        qs = qs.filter(
            Q(work_order_number__icontains=q)
            | Q(customer__first_name__icontains=q)
            | Q(customer__last_name__icontains=q)
            | Q(customer__email__icontains=q)
            | Q(customer__phone_number__icontains=q)
        )
    if status:
        qs = qs.filter(status=status)
    if customer:
        qs = qs.filter(
            Q(customer__first_name__icontains=customer)
            | Q(customer__last_name__icontains=customer)
        )
    if start_date:
        qs = qs.filter(date_received__gte=parse_date(start_date))
    if end_date:
        qs = qs.filter(date_received__lte=parse_date(end_date))

    paginator = Paginator(qs.order_by("-date_received"), 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "workorders": page_obj,
        "status_choices": WorkOrder.STATUS_CHOICES,
        "page_obj": page_obj,
    }
    return render(request, "workshop/search.html", context)


# ─────────────────────────────
# DRF ViewSets
# ─────────────────────────────
class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["first_name", "last_name", "email", "phone_number"]
    ordering_fields = ["first_name", "last_name"]


class TechnicianViewSet(viewsets.ModelViewSet):
    queryset = Technician.objects.all()
    serializer_class = TechnicianSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["first_name", "last_name", "email", "phone_number"]
    ordering_fields = ["first_name", "last_name"]


class WorkOrderViewSet(viewsets.ModelViewSet):
    queryset = WorkOrder.objects.filter(is_active=True).select_related("customer", "technician")
    serializer_class = WorkOrderSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = WorkOrderFilter
    search_fields = [
        "work_order_number",
        "customer__first_name",
        "customer__last_name",
        "customer__email",
        "customer__phone_number",
        "technician__first_name",
        "technician__last_name",
        "product_type",
        "product_brand",
        "serial_number",
    ]
    ordering_fields = ["date_created", "status", "product_brand", "total_cost"]
    ordering = ["-date_created"]

    @action(detail=True, methods=["post"])
    def mark_repaired(self, request, pk=None):
        work_order = self.get_object()
        work_order.is_repaired = True
        work_order.status = "completed"
        work_order.save()
        return Response({"status": "Work order marked as repaired"})

    @action(detail=True, methods=["post"])
    def mark_collected(self, request, pk=None):
        work_order = self.get_object()
        work_order.customer_collected = True
        work_order.collected_at = timezone.now()
        work_order.save()
        return Response({"status": f"{work_order.work_order_number} marked as collected"})

    @action(detail=False, methods=["post"])
    def bulk_update(self, request):
        ids = request.data.get("ids", [])
        status = request.data.get("status")
        technician_id = request.data.get("technician_id")
        qs = WorkOrder.objects.filter(id__in=ids, is_active=True)
        updates = {}
        if status:
            updates["status"] = status
        if technician_id:
            updates["technician_id"] = technician_id
        count = qs.update(**updates)
        return Response({"updated_records": count})

    @action(detail=False, methods=["post"])
    def bulk_archive(self, request):
        ids = request.data.get("ids", [])
        qs = WorkOrder.objects.filter(id__in=ids, is_active=True)
        count = qs.update(is_active=False)
        return Response({"archived_records": count})


class ProductImageViewSet(viewsets.ModelViewSet):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["uploaded_at"]
