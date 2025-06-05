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



# forms.py
from django import forms
from .models import StudentProfile, FeeStructure

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

class MultiInvoiceForm(forms.Form):
    term = forms.ChoiceField(choices=TERM_CHOICES)
    class_level = forms.ChoiceField(choices=LEVEL_CHOICES)
    all_fitting_students = forms.BooleanField(required=False, label="All Fitting Students")
    students = forms.ModelMultipleChoiceField(
        queryset=StudentProfile.objects.none(),
        required=False
    )
    fee_structures = forms.ModelMultipleChoiceField(
        queryset=FeeStructure.objects.none()
    )
    due_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'term' in self.data and 'class_level' in self.data:
            term = self.data.get('term')
            class_level = self.data.get('class_level')
            self.fields['students'].queryset = StudentProfile.objects.filter(term=term, class_level=class_level)
            self.fields['fee_structures'].queryset = FeeStructure.objects.filter(term=term, class_level=class_level)
        else:
            self.fields['students'].queryset = StudentProfile.objects.none()
            self.fields['fee_structures'].queryset = FeeStructure.objects.none()
