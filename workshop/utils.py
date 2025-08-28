# workshop/utils.py
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.core.cache import cache

def send_status_update_email(workorder):
    """
    Send status update notification to the customer via email.
    """
     # Rate limiting: only send one email per workorder per 5 minutes
    cache_key = f"email_sent_{workorder.id}_{workorder.status}"
    if cache.get(cache_key):
        print(f"⏸️  Email already sent recently for {workorder.work_order_number}")
        return False
    # Ensure customer has a valid email
    customer_email = workorder.customer.email if workorder.customer else None
    if not customer_email:
        print(f"No customer email for WorkOrder {workorder.work_order_number}")
        return False

    # Build full name
    customer_name = f"{workorder.customer.first_name} {workorder.customer.last_name}"

    context = {
        "customer_name": customer_name,
        "workorder": workorder,
        "status": workorder.status,
    }

    subject = f"Update on Your Service Request #{workorder.work_order_number}"
    html_content = render_to_string("workshop/email/status_update.html", context)

    msg = EmailMultiAlternatives(
        subject,
        f"Your service request {workorder.work_order_number} status has changed to {workorder.status}.",
        settings.DEFAULT_FROM_EMAIL,
        [customer_email],
    )
    msg.attach_alternative(html_content, "text/html")

    try:
        msg.send()
        print(f"✅ Status update email sent to {customer_email}")
        return True
    except Exception as e:
        print(f"❌ Failed to send status email: {e}")
        return False



def send_sms(to, message):
    """
    SMS sending is currently disabled.
    This is a safe stub that just logs to console.
    """
    print(f"[SMS DISABLED] Would send SMS to {to}: {message}")
