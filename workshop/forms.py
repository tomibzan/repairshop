from django import forms
from .models import RemoteRequest

class RemoteRequestForm(forms.ModelForm):
    class Meta:
        model = RemoteRequest
        fields = [
            "customer_name",
            "customer_email",
            "customer_phone",
            "issue_description",
            "preferred_datetime",
        ]
        widgets = {
            "issue_description": forms.Textarea(attrs={"rows": 4}),
            "preferred_datetime": forms.TextInput(attrs={"placeholder": "Optional: YYYY-MM-DD HH:MM"}),
        }
        labels = {
            "customer_name": "Full Name",
            "customer_email": "Email Address",
            "customer_phone": "Phone Number",
            "issue_description": "Describe your problem",
            "preferred_datetime": "Preferred Date/Time (Optional)",
        }
