from billing.views import get_dashboard_context
from django.urls import reverse
from django.http import JsonResponse, HttpResponseForbidden
from django.utils.timezone import now
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages
from django.db.models import Q, Sum
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.sites.shortcuts import get_current_site
from .tokens import account_activation_token
from .forms import UserRegistrationForm, CustomUserForm
from .models import Notification, UserNotificationStatus
import datetime
from billing.models import StudentProfile, Payment, PaymentMethod, Invoice
from django.utils import timezone
from datetime import datetime, date
from functools import wraps
from django.template.loader import render_to_string
from weasyprint import HTML

User = get_user_model()

def parents_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and not request.user.is_parent:
            return render(request, "yuzzaz/403.html")
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def register(request, user_type):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Deactivate account until email verification
            # Set user type based on URL parameter
            if user_type == "parent":
                user.is_parent = True
            else:
                user.is_parent = False  # Default to cohort
            
            user.save()

            # Send activation email
            current_site = get_current_site(request)
            mail_subject = "Activate your user account"
            message = render_to_string("yuzzaz/activate_account.html", {
                'user': user,
                'domain': current_site.domain,
                'protocol': 'https' if request.is_secure() else 'http',
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
                # 'current_year': datetime.datetime.now().year,
                'current_year': datetime.now().year,

            })
            email = EmailMessage(mail_subject, message, to=[user.email])
            email.content_subtype = "html"  # Ensure the email content type is HTML
            email.send()

            messages.success(
                request, f"Dear {user.first_name}, we have sent an activation link to your email. Please check your email to complete registration (Remember to check your spam too, you can't proceed without that email)."
            )
            request.session['inactive_user_email'] = user.email  # Store for resend logic
            return redirect('activation_sent')

            # return redirect('homepage')  # Redirect to login page
    else:
        form = UserRegistrationForm()

    return render(request, 'yuzzaz/register.html', {'form': form, 'user_type': user_type})


# Activate view: Handles the account activation via the token
def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Thank you for confirming your email. You can now log in.")
        return redirect('login')
    else:
        messages.error(request, "Activation link is invalid.")
        return redirect('homepage')


def login(request, user_type=None):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user:
            auth_login(request, user)
            messages.success(request, "You have successfully logged in.")

            if user.is_parent:
                return redirect('parents_dashboard')
            elif user.is_staff:
                return redirect('staff_dashboard')
            else:
                return redirect('student_dashboard')

        else:
            # Try to fetch inactive user to provide better feedback
            try:
                user_obj = User.objects.get(email=username)
                if not user_obj.is_active and user_obj.check_password(password):
                    request.session['inactive_user_email'] = user_obj.email
                    request.session['email_sent_time'] = datetime.now().isoformat()

                    messages.warning(request, "Your account is not activated. Please check your email or request a new activation link.")
                    return redirect('activation_sent')
            except User.DoesNotExist:
                pass  # Fall through to invalid credentials message

            messages.error(request, "Invalid credentials, please try again.")

    return render(request, 'yuzzaz/login.html', {'user_type': user_type})



@login_required
def post_login_redirect(request):
    user = request.user
    if user.is_staff:
        return redirect('staff_dashboard')
    elif user.is_parent:
        return redirect('parents_dashboard')
    else:
        return redirect('student_dashboard')


@login_required
@parents_required
def parents_dashboard(request):
    parent = request.user

    recent_payments = Payment.objects.filter(
        invoice__student__parent=parent,
        # invoice__status__in=['Paid', 'Partial']
    ).select_related('invoice', 'invoice__student').order_by('-payment_date')[:5]

    all_pending_invoices = Invoice.objects.filter(
        student__parent=parent,
        status__in=['Unpaid', 'Partial']
    ).order_by('-due_date')

    all_invoices = Invoice.objects.filter(
        student__parent=parent,
        status__in=['Unpaid', 'Partial', 'Fully Paid']
    ).order_by('-due_date')

    pending_invoices = Invoice.objects.filter(
        student__parent=parent,
        status__in=['Unpaid', 'Partial']
    ).order_by('-due_date')[:5]

    # total_due = pending_invoices.aggregate(total=Sum('total_amount'))['total'] or 0
    total_due = all_invoices.aggregate(total=Sum('total_amount'))['total'] or 0

    term_paid_total = Payment.objects.filter(
    invoice__student__parent=parent,
    # invoice__term=term_name  # replace with desired term string
    ).aggregate(total=Sum('amount'))['total'] or 0

    # all_invoices = Invoice.objects.filter(student__parent=parent)
    # total_paid = Payment.objects.filter(
    #     invoice__in=all_invoices
    # ).aggregate(total=Sum('amount'))['total'] or 0

    pending_total = total_due - term_paid_total
    if total_due > 0:
        rem_percent = (pending_total / total_due) * 100
    else:
        rem_percent = 0

    pendings_count = Invoice.objects.filter(
        student__parent=parent,
        status__in=['Unpaid', 'Partial']
    ).count()

    overdue_count = Invoice.objects.filter(
    student__parent=parent,
    status__in=['Unpaid', 'Partial'],
    due_date__lt=now().date()
    ).count()

    unpaid_invoices = Invoice.objects.filter(
        student__parent=parent,
        status__in=['Unpaid', 'Partial']
    ).select_related('student')

    upcoming_invoices = unpaid_invoices.order_by('due_date')[:5]  # limit if needed
    
    notifications = Notification.objects.filter(Q(is_public=True) | Q(user=request.user)).distinct()
    read_ids = set(UserNotificationStatus.objects.filter(
    user=request.user,
    is_read=True,
    notification__in=notifications
    ).values_list('notification_id', flat=True))

    for note in notifications:
        note.is_unread = note.id not in read_ids

    user_notifications = request.user.notifications.filter(is_public=True)
    has_unread_notifications = any(
    not UserNotificationStatus.objects.filter(user=request.user, notification=note, is_read=True).exists()
    for note in notifications
    )
    unread_notification = UserNotificationStatus.objects.filter(user=request.user, notification__in=notifications, is_read=False).exists()
    unread_count = sum(1 for note in notifications if note.is_unread)

    context = {
        'user': request.user,
        'students': StudentProfile.objects.filter(parent=parent),
        'methods': request.user.payment_methods.all(),
        'recent_payments' : recent_payments,
        'pending_total': pending_total,
        'pendings_count': pendings_count,
        'overdue_count': overdue_count,
        'paid_total': term_paid_total,
        'rem_percent': rem_percent,
        'today': date.today(),
        'upcoming_invoices': upcoming_invoices,
        'all_pending_invoices': all_pending_invoices,
        'notifications': notifications,
        'has_unread_notifications': has_unread_notifications,
        'unread_notification': unread_notification,
        'unread_count': unread_count,
    }
    return render(request, 'yuzzaz/parents_dashboard.html', context)



@login_required
def mark_all_notifications_as_read(request):
    notifications = Notification.objects.filter(user=request.user) | Notification.objects.filter(is_public=True)
    for notification in notifications:
        status, _ = UserNotificationStatus.objects.get_or_create(user=request.user, notification=notification)
        if not status.is_read:
            status.is_read = True
            status.read_at = now()
            status.save()
    return JsonResponse({'status': 'success', 'message': 'All notifications marked as read.'})

@login_required
def mark_all_notifications_as_read_page(request):
    notifications = Notification.objects.filter(user=request.user) | Notification.objects.filter(is_public=True)
    for notification in notifications:
        status, _ = UserNotificationStatus.objects.get_or_create(user=request.user, notification=notification)
        if not status.is_read:
            status.is_read = True
            status.read_at = now()
            status.save()
    messages.success(request, "All notifications have been marked as read.")
    return redirect(request.META.get('HTTP_REFERER', 'notifications')) 

@login_required
def profile(request):
    user = request.user  # Get the current logged-in user
    if request.method == 'POST':
        form = CustomUserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated!")
            return redirect('profile')  # Redirect to the same page
    else:
        form = CustomUserForm(instance=user)
    context = {
        'user': user,
        'form': form
    }    
    context.update(get_dashboard_context(request))
    return render(request, 'yuzzaz/profile.html', context)


def homepage(request):
    now = timezone.now()
    open_date = timezone.make_aware(datetime(2025, 4, 26))
    close_date = timezone.make_aware(datetime(2025, 6, 26))
    portal_open = open_date <= now < close_date
    return render(request, 'yuzzaz/homepage.html', {
        'portal_open': portal_open
    })


def logout(request):
    auth_logout(request)
    messages.success(request, "You have successfully logged out.")
    return redirect('login')

def counsellor_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_counsellor:
            return HttpResponseForbidden("You are not authorized to access this page. Please login as a counsellor.")
        return view_func(request, *args, **kwargs)
    return wrapper



@user_passes_test(lambda u: u.is_staff)
def activate_all_users(request):
    inactive_users = User.objects.filter(is_active=False)
    # inactive_users = User.objects.filter(is_active=False, application__submitted=False)
    count = inactive_users.count()

    for user in inactive_users:
        user.is_active = True
        user.save()

    messages.success(request, f"Successfully activated {count} inactive user(s).")
    return redirect('intern_view_all_applications')  # Change to your desired redirect URL
    

@user_passes_test(lambda u: u.is_staff)
@require_POST
def activate_user_by_email(request):
    email = request.POST.get('email')
    user = User.objects.filter(email=email).first()

    if user:
        if user.is_active:
            messages.info(request, f"User '{email}' is already active.")
        else:
            user.is_active = True
            user.save()
            messages.success(request, f"User '{email}' has been activated.")
    else:
        messages.error(request, f"No user found with email '{email}'.")

    return redirect('intern_view_all_applications')





# views.py
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import BulkEmailForm
from .models import CustomUser
from django.template.loader import render_to_string


def is_staff_user(user):
    return user.is_staff

@login_required
@user_passes_test(is_staff_user)
def send_custom_email(request):
    if request.method == 'POST':
        form = BulkEmailForm(request.POST, request.FILES)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            heading = form.cleaned_data['heading']
            content = form.cleaned_data['content']
            content1 = form.cleaned_data['content1']
            content2 = form.cleaned_data['content2']
            attachment = form.cleaned_data.get('attachment')
            send_to_all = form.cleaned_data['send_to_all']
            selected_users = form.cleaned_data['selected_users']

            if send_to_all:
                recipients = CustomUser.objects.all()
            else:
                recipients = selected_users

            for user in recipients:
                context = {
                    'full_name': user.get_full_name(),
                    'user': user,
                    'heading': heading,
                    'content': content,
                    'content1': content1,
                    'content2': content2,
                }
                html_content = render_to_string('emails/custom_email.html', context)
                plain_content = strip_tags(html_content)

                email = EmailMultiAlternatives(subject, plain_content, to=[user.email])
                email.attach_alternative(html_content, "text/html")

                if attachment:
                    email.attach(attachment.name, attachment.read(), attachment.content_type)

                email.send()

            messages.success(request, "Emails have been sent successfully!")
            return redirect('intern_view_all_applications')
        else:
            messages.error(request, "Please correct the errors in the form.")
    else:
        form = BulkEmailForm()

    return render(request, 'emails/send_custom_email.html', {'form': form})

def set_user_type_and_login(request, user_type):
    request.session['login_user_type'] = user_type
    return redirect(f"{reverse('social:begin', args=['google-oauth2'])}?next=/post-login/")









from django.utils.timezone import now
from datetime import timedelta

def activation_sent(request):
    email = request.session.get('inactive_user_email')
    if not email:
        return redirect('register', user_type='parent')  # Or fallback

    # Store the timestamp if not set
    if not request.session.get('email_sent_time'):
        request.session['email_sent_time'] = now().isoformat()

    return render(request, 'yuzzaz/activation_sent.html', {
        'email': email,
        'can_resend_at': now() + timedelta(seconds=90)
    })


def resend_activation_email(request):
    email = request.session.get('inactive_user_email')
    sent_time = request.session.get('email_sent_time')

    if not email or not sent_time:
        messages.error(request, "Session expired. Please register again.")
        return redirect('register', user_type='parent')

    if (now() - datetime.fromisoformat(sent_time)).total_seconds() < 90:
        messages.warning(request, "Please wait before requesting a new email.")
        return redirect('activation_sent')

    user = User.objects.filter(email=email, is_active=False).first()
    if user:
        current_site = get_current_site(request)
        message = render_to_string("yuzzaz/activate_account.html", {
            'user': user,
            'domain': current_site.domain,
            'protocol': 'https' if request.is_secure() else 'http',
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': account_activation_token.make_token(user),
            'current_year': datetime.now().year,
        })
        email_obj = EmailMessage("Activate your user account", message, to=[user.email])
        email_obj.content_subtype = "html"
        email_obj.send()

        request.session['email_sent_time'] = now().isoformat()
        messages.success(request, "A new activation link has been sent.")
    else:
        messages.error(request, "No inactive account found with that email.")
    return redirect('activation_sent')
