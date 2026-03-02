from django.contrib import admin
from .models import Complaint
from .models import UserRegister
from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings




admin.site.register(UserRegister)

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'user', 'status', 'issue_date')

    def save_model(self, request, obj, form, change):
        old_status = None

        if change:
            old_status = Complaint.objects.get(pk=obj.pk).status

        super().save_model(request, obj, form, change)

        # 📧 Send mail when status becomes Resolved
        if old_status != obj.status and obj.status.lower() == "resolved":
            status_url = request.build_absolute_uri(
                reverse('complaint_status', args=[obj.id])
            )

            send_mail(
                subject="Your Complaint Has Been Resolved ✅",
                message=f"""
Hello {obj.user.username},

Your complaint "{obj.title}" has been RESOLVED.

👉 Check your complaint status here:
{status_url}

Thank you for using our service.
""",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[obj.user.email],
                fail_silently=False,
            )
