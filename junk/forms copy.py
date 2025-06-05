from django import forms
from .models import FeeStructure, Invoice, StudentProfile, User
from django.contrib.auth import get_user_model

User = get_user_model()

class FeeStructureForm(forms.ModelForm):
    class Meta:
        model = FeeStructure
        fields = ['class_level', 'term', 'fee_name', 'amount', 'effective_date']
        widgets = {
            'class_level': forms.Select(attrs={
                'class': 'select-field',
                'placeholder': 'Select class level'
            }),
            'term': forms.Select(attrs={
                'class': 'select-field',
                'placeholder': 'Select term'
            }),
            'fee_name': forms.TextInput(attrs={
                'placeholder': 'Enter fee name (e.g. Tuition, Activity)'
            }),
            'amount': forms.NumberInput(attrs={
                'placeholder': 'Amount in TZS',
                'min': '0',
                'step': '1000'
            }),
            'effective_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'date-field'
            }),
        }
        labels = {
            'fee_name': 'Fee Description',
            'amount': 'Amount (TZS)',
        }

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['student', 'term', 'due_date', 'total_amount', 'fee_structures']
        widgets = {
            'student': forms.Select(attrs={
                'class': 'select-field',
                'data-placeholder': 'Select student'
            }),
            'term': forms.Select(attrs={
                'class': 'select-field'
            }),
            'due_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'date-field'
            }),
            'total_amount': forms.NumberInput(attrs={
                'placeholder': 'Auto-calculated if fees selected',
                'readonly': 'readonly',
                'class': 'bg-gray-100'
            }),
            'fee_structures': forms.SelectMultiple(attrs={
                'class': 'select-multiple-field',
                'data-placeholder': 'Select applicable fees'
            }),
        }
        help_texts = {
            'total_amount': 'Will be calculated automatically when you select fee structures',
        }

class StudentProfileForm(forms.ModelForm):
    user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        label="User Account",
        widget=forms.Select(attrs={
            'class': 'select-field',
            'data-placeholder': 'Select user account'
        })
    )

    class Meta:
        model = StudentProfile
        fields = ['user', 'parent', 'class_level']
        widgets = {
            'parent': forms.Select(attrs={
                'class': 'select-field',
                'data-placeholder': 'Select parent/guardian'
            }),
            'class_level': forms.Select(attrs={
                'class': 'select-field'
            }),
        }







class ParentContactForm(forms.Form):
    parent_contact = forms.EmailField(
        label="Your parent’s official email",
        widget=forms.EmailInput(attrs={
            'class': 'w-full mt-1 p-2 border rounded-lg',
            'placeholder': 'parent@example.com'
        })
    )
