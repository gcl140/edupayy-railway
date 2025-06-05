from django.utils import timezone
from decimal import Decimal
import stripe
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from .models import Payment, StudentProfile, Invoice
from yuzzaz.models import Notification, UserNotificationStatus
from django.contrib.auth.decorators import login_required
from django.db.models import Q

stripe.api_key = settings.STRIPE_SECRET_KEY
webhook = whsec_673880a1b88347d0074e5f160ec587b80dd6bb2b8b5f75e6bc890df3ba70fc30 
@login_required
def download_receipt(request, payment_id):
    payment = Payment.objects.select_related('invoice__student__user').get(id=payment_id)

    html_string = render_to_string("billing/receipt_template.html", {
        "payment": payment
    })

    html = HTML(string=html_string)
    pdf = html.write_pdf()

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="receipt-{payment.id}.pdf"'
    return response

@login_required
def download_invoice_pdf(request, invoice_id):
    invoice = Invoice.objects.select_related('student__user').prefetch_related('invoice_fees__fee_structure').get(id=invoice_id)

    html_string = render_to_string("billing/invoice_template.html", {
        "invoice": invoice,
        "student": invoice.student,
        "fees": invoice.invoice_fees.all(),
    })

    pdf = HTML(string=html_string).write_pdf()

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice-{invoice.id}.pdf"'
    return response

def payments_history(request):
    parent = request.user

    all_payments = Payment.objects.filter(
        invoice__student__parent=parent,
        # invoice__status__in=['Paid', 'Partial']
    ).select_related('invoice', 'invoice__student').order_by('-payment_date')

    context = {
        'user': request.user,
        'students': StudentProfile.objects.filter(parent=parent),
        'methods': request.user.payment_methods.all(),
        'recent_payments' : all_payments,
    }
    return render(request, 'billing/payments_history.html', context)

def invoices(request):
    parent = request.user

    all_invoices = Invoice.objects.filter(
        student__parent=parent,
    ).select_related('student').order_by('-due_date')

    context = {
        'user': request.user,
        'students': StudentProfile.objects.filter(parent=parent),
        'methods': request.user.payment_methods.all(),
        'all_invoices' : all_invoices,
    }
    return render(request, 'billing/invoices.html', context)

def students(request):
    parent = request.user
    students = StudentProfile.objects.filter(parent=parent).select_related('user').order_by('-balance')
    for student in students:
        invoices = student.invoices.all()
        student.paid_count = invoices.filter(status="Fully Paid").count()
        student.unpaid_count = invoices.filter(status__in=["Unpaid", 'Partial']).count()
    context = {
        'students': students,
        'user': parent,
    }
    return render(request, 'billing/students.html', context)

@login_required
def notifications(request):
    notifications = Notification.objects.filter(
        Q(is_public=True) | Q(user=request.user)
    ).distinct().order_by('-created_at')
    
    # Get read notification IDs for the current user
    read_ids = set(UserNotificationStatus.objects.filter(
        user=request.user,
        is_read=True,
        notification__in=notifications
    ).values_list('notification_id', flat=True))
    
    # Add is_unread flag to each notification
    for note in notifications:
        note.is_unread = note.id not in read_ids
    
    # Count unread notifications
    unread_count = sum(1 for note in notifications if note.is_unread)
    
    context = {
        'notifications': notifications,
        'unread_count': unread_count,
        'user': request.user,
    }
    return render(request, 'billing/notifications.html', context)


@login_required
def unread_notifications_api(request):
    notifications = Notification.objects.filter(
        Q(is_public=True) | Q(user=request.user)
    ).distinct().order_by('-created_at')

    read_ids = set(UserNotificationStatus.objects.filter(
        user=request.user,
        is_read=True,
        notification__in=notifications
    ).values_list('notification_id', flat=True))

    unread = [
        {
            'id': note.id,
            'title': note.title,
            'message': note.message,
            'created_at': note.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        }
        for note in notifications if note.id not in read_ids
    ]

    return JsonResponse({'unread_notifications': unread})







def checkout_page(request):
    return render(request, 'billing/checkout.html')


# views.py
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal
import stripe
import json
from datetime import datetime
from .models import Payment, Invoice

stripe.api_key = settings.STRIPE_SECRET_KEY

@csrf_exempt
def create_checkout_session(request, invoice_id):
    invoice = get_object_or_404(Invoice, pk=invoice_id)
    
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'tzs',
                    'product_data': {
                        'name': f'Tuition - {invoice.term}',
                    },
                    'unit_amount': int(invoice.total_amount * 100),  # convert to cents
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=f"{request.build_absolute_uri('/billing/payment_success/')}?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=request.build_absolute_uri('/billing/payment_cancel/'),
            metadata={
                'invoice_id': str(invoice.id),
                'student_id': str(invoice.student.id),
                'user_id': str(request.user.id),
            }
        )
        return redirect(session.url, code=303)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

# @csrf_exempt
# def stripe_webhook(request):
#     payload = request.body
#     sig_header = request.META['HTTP_STRIPE_SIGNATURE']
#     event = None

#     try:
#         event = stripe.Webhook.construct_event(
#             payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
#         )
#     except ValueError as e:
#         return HttpResponse(status=400)
#     except stripe.error.SignatureVerificationError as e:
#         return HttpResponse(status=400)

#     if event['type'] == 'checkout.session.completed':
#         session = event['data']['object']
        
#         # Handle the successful payment
#         handle_successful_payment(session)

#     return HttpResponse(status=200)

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    webhook_secret = settings.STRIPE_WEBHOOK_SECRET
    event = None

    if sig_header is None:
        return HttpResponse(status=400)

    try:
        event = stripe.Webhook.construct_event(
            payload=payload, sig_header=sig_header, secret=webhook_secret
        )
    except ValueError:
        return HttpResponse(status=400)  # Invalid payload
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)  # Invalid signature

    # Handle specific event types
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        handle_successful_payment(session)  # your custom logic

    return HttpResponse(status=200)

    
def handle_successful_payment(session):
    invoice_id = session.metadata.get('invoice_id')
    student_id = session.metadata.get('student_id')
    user_id = session.metadata.get('user_id')
    
    invoice = Invoice.objects.get(id=invoice_id)
    amount = Decimal(session.amount_total) / 100  # Convert back from cents
    
    # Create payment record
    payment = Payment.objects.create(
        invoice=invoice,
        amount=amount,
        method='Stripe',
        transaction_id=session.payment_intent,
    )
    
    # Update invoice status if needed
    if invoice.balance <= amount:
        invoice.status = 'Fully Paid'
    else:
        invoice.status = 'Partial'
    invoice.save()

def payment_success(request):
    session_id = request.GET.get('session_id')
    
    if not session_id:
        return redirect('payment_cancel')
    
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        payment_intent = stripe.PaymentIntent.retrieve(session.payment_intent)
        
        # Get last4 digits of card if available
        payment_method = stripe.PaymentMethod.retrieve(payment_intent.payment_method)
        last4 = payment_method.card.last4 if payment_method.card else 'card'
        
        context = {
            'amount': Decimal(session.amount_total) / 100,
            'transaction_id': session.payment_intent,
            'payment_date': datetime.fromtimestamp(session.created),
            'payment_method': f"{payment_method.card.brand.title()} ending in {last4}" if payment_method.card else "Credit Card",
            'invoice': Invoice.objects.get(id=session.metadata.invoice_id),
        }
        
        return render(request, 'billing/success.html', context)
    except Exception as e:
        return redirect('payment_cancel')