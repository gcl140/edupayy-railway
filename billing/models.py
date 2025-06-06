from random import choices
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    parent = models.ForeignKey(User, on_delete=models.CASCADE, related_name='parent_students', null=True, blank=True, limit_choices_to={'is_parent': True})
    admission_number = models.CharField(max_length=20, unique=True)

    LEVEL_CHOICES = [
        ('Grade 1','Grade 1'),
        ('Grade 7','Grade 7'),
        ('Form 1','Form 1'),
        ('Form 4','Form 4'),
        ('Form 6','Form 6'),
        ('UG','UG'),
        ('Grad','Grad'),
    ]
    TERM_CHOICES = [
        ('Term 1', 'Term 1'),
        ('Term 2', 'Term 2'),
    ]
    class_level = models.CharField(max_length=50, choices=LEVEL_CHOICES)
    term = models.CharField(max_length=20, choices=TERM_CHOICES)
    parent_contact = models.EmailField()

    @property
    def balance(self):
        from django.db.models import Sum
        invoices = self.invoices.filter(status__in=['Unpaid', 'Partial'])
        total_due = invoices.aggregate(total=Sum('total_amount'))['total'] or 0
        return total_due

    def __str__(self):
        parent_name = self.parent.get_full_name() if self.parent else "No Parent"
        return f"{self.user.get_full_name()} - {parent_name} - {self.class_level}"



class ParentRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    parent = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'is_parent': True})
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.user.get_full_name()} → {self.parent.get_full_name()} ({self.status})"

class FeeStructure(models.Model):
    TERM_CHOICES = [
        ('Term 1', 'Term 1'),
        ('Term 2', 'Term 2'),
    ]
    LEVEL_CHOICES = [
        ('Grade 1','Grade 1'),
        ('Grade 7','Grade 7'),
        ('Form 1','Form 1'),
        ('Form 4','Form 4'),
        ('Form 6','Form 6'),
        ('UG','UG'),
        ('Grad','Grad'),
    ]
    class_level = models.CharField(max_length=50, choices=LEVEL_CHOICES)
    term = models.CharField(max_length=20, choices=TERM_CHOICES)
    fee_name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    effective_date = models.DateField()

    def __str__(self):
        return f"{self.class_level} - {self.term} - {self.fee_name}"


class Invoice(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="invoices")
    TERM_CHOICES = [
        ('Term 1', 'Term 1'),
        ('Term 2', 'Term 2'),
    ]
    term = models.CharField(max_length=20, choices=TERM_CHOICES)
    issue_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[('Fully Paid', 'Fully Paid'), ('Unpaid', 'Unpaid'), ('Partial', 'Partial')], default='Unpaid')
    
    fee_structures = models.ManyToManyField(FeeStructure, through='InvoiceFee')

    def __str__(self):
        return f"Invoice {self.id} - {self.student.user.get_full_name()}"

class InvoiceFee(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='invoice_fees')
    fee_structure = models.ForeignKey(FeeStructure, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Allows adjustment if needed

    def __str__(self):
        return f"{self.invoice} - {self.fee_structure.fee_name} - {self.amount}"

class Payment(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    method = models.CharField(max_length=50)
    transaction_id = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Payment {self.id} - {self.amount}"


class PaymentMethod(models.Model):
    PAYMENT_TYPE_CHOICES = [
        ('Card', 'Card'),
        ('MobileMoney', 'Mobile Money'),
        ('BankTransfer', 'Bank Transfer'),
        ('PayPal', 'PayPal'),
        # Add more as needed
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payment_methods")
    payment_type = models.CharField(max_length=30, choices=PAYMENT_TYPE_CHOICES)
    provider = models.CharField(max_length=50)  # e.g., "Visa", "MTN", "Vodafone"
    account_name = models.CharField(max_length=100, blank=True)  # Optional display name
    account_number = models.CharField(max_length=20)  # e.g., last 4 digits or mobile number
    expiry_date = models.DateField(blank=True, null=True)  # Only for cards
    is_default = models.BooleanField(default=False)
    added_on = models.DateTimeField(auto_now_add=True)

    def masked_account(self):
        return f"****{self.account_number[-4:]}" if self.account_number else ""

    def __str__(self):
        return f"{self.provider} ({self.masked_account()})"



