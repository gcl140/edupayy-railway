from django.contrib.auth import views as auth_views
from django.urls import path
from . import views


urlpatterns = [
    path('download_receipt/<int:payment_id>/', views.download_receipt, name='download_receipt'),
    path('download_invoice_pdf/<int:invoice_id>/', views.download_invoice_pdf, name='download_invoice_pdf'),
    path('payments_history/', views.payments_history, name='payments_history'),
    path('invoices/', views.invoices, name='invoices'),
    path('students/', views.students, name='students'),
    path('notifications/', views.notifications, name='notifications'),
    path('api/unread-notifications/', views.unread_notifications_api, name='unread_notifications_api'),
    path('checkout_page/', views.checkout_page, name='checkout_page'), 
    # path('create_checkout_session/', views.create_checkout_session, name='create_checkout_session'),
    path('checkout/<int:invoice_id>/', views.create_checkout_session, name='create_checkout_session'),
    path('payment_success/', views.payment_success, name='payment_success'),
    path('payment_cancel/', views.payment_cancel, name='payment_cancel'),
    path('staff_dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('feesstructures/', views.feesstructures, name='feesstructures'),
    path('staff/student/<int:student_id>/dashboard/', views.student_detail_dashboard, name='student_detail_dashboard'),


    path('fee-structure/create/', views.create_fee_structure, name='create_fee_structure'),
    path('invoice/create/', views.create_invoice, name='create_invoice'),
    # path('student/create/', views.create_student, name='create_student'),
    # path('payment/create/', views.record_payment, name='record_payment'),

    # path('stripe/webhook/', views.stripe_webhook, name='stripe-webhook'),
    path('export/payments/csv/', views.export_payments_csv, name='export_payments_csv'),

    path('export/payments/excel/', views.export_payments_excel, name='export_payments_excel'),
    path('tables/', views.tables, name='tables'),



    path('dashboard/', views.student_dashboard, name='student_dashboard'),
    path('link-parent/', views.link_parent_request, name='link_parent_request'),
    path('parent/respond/<int:req_id>/<str:action>/', views.respond_parent_request, name='respond_parent_request'),

    path('payment_status_check/', views.payment_status_check, name='payment_status_check'),
    path('create_bulk_invoices/', views.create_bulk_invoices, name='create_bulk_invoices'),
    path('load_invoice_form_options/', views.load_invoice_form_options, name='load_invoice_form_options'),



]
