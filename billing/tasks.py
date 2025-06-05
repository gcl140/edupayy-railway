from datetime import datetime
from django.contrib.sites.shortcuts import get_current_site
# from django.contrib.sites.models import Site
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from celery import shared_task
from django.core.mail import send_mail
from .models import Invoice
from django.urls import reverse

payment_link = reverse('parents_dashboard')

@shared_task
def send_invoice_reminders():

    domain = 'localhost:8000'  # Replace with actual domain
    protocol = 'http'  # Or 'http' if not using SSL

    invoices = Invoice.objects.filter(status__in=['Partial', 'Unpaid'])
    for invoice in invoices:
        student = invoice.student
        parent = student.parent

        recipient_email = parent.email if parent and parent.email else student.user.email
        
        payment_link = f"{protocol}://{domain}{reverse('parents_dashboard')}"

        context = {
            'student_name': student.user.get_full_name(),
            'amount': invoice.total_amount,
            'due_date': invoice.due_date,
            'invoice_id': invoice.id,
            'payment_link': payment_link,
            'protocol': protocol,
            'domain': domain,
            'current_year': datetime.now().year,
        }

        subject = '📢 Pending Invoice Reminder'
        from_email = settings.EMAIL_HOST_USER  # or 'noreply@yourdomain.com'
        text_body = render_to_string('emails/invoice_reminder.txt', context)
        html_body = render_to_string('emails/invoice_reminder.html', context)

        msg = EmailMultiAlternatives(subject, text_body, from_email, [recipient_email])
        msg.attach_alternative(html_body, "text/html")
        msg.send()

