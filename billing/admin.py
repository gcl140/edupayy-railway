from django.contrib import admin
from .models import FeeStructure, Invoice, Payment, StudentProfile, PaymentMethod, InvoiceFee, ParentRequest

class InvoiceFeeInline(admin.TabularInline):
    model = InvoiceFee
    extra = 1

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    inlines = [InvoiceFeeInline]
    list_display = ('student', 'term', 'issue_date', 'due_date', 'total_amount', 'status')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('invoice', 'amount', 'payment_date', 'method', 'transaction_id')

@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
    list_display = ('class_level', 'term', 'fee_name', 'amount', 'effective_date')

@admin.register(ParentRequest)
class ParentRequestAdmin(admin.ModelAdmin):
    list_display = ('student', 'parent', 'status')

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'admission_number', 'class_level', 'parent_contact')

@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('user', 'payment_type', 'provider', 'masked_account', 'is_default', 'added_on')
    list_filter = ('payment_type', 'provider', 'is_default')
    search_fields = ('user__email', 'account_number', 'provider')


admin.site.register(InvoiceFee)