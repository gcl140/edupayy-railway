from django import forms
from .models import CustomUser


class UserRegistrationForm(forms.ModelForm):
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
        label="Password"
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}),
        label="Confirm Password"
    )
    is_parent = forms.BooleanField(
        required=False, 
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input custom-checkbox',  
            'style': 'width: 20px; height: 20px; accent-color: gold; margin-right: 8px;',
            'aria-label': 'Internship Position'  # Alternative for accessibility
        })
    )



    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'is_parent']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'phone_number': forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+255 XXX XXX XXX'
            }),
        }

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match!")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.username = self.cleaned_data["email"]  # Set the username to email
        user.is_parent = self.cleaned_data.get("is_parent", False)  # Save the internship preference
        if commit:
            user.save()
        return user


class CustomUserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'profile_picture']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
        }




class BulkEmailForm(forms.Form):
    subject = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Subject'}))
    heading = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Heading'}))
    content = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 6, 'placeholder': 'Main message'}))
    content1 = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 6, 'placeholder': 'Main message'}))
    content2 = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 6, 'placeholder': 'Main message'}))
    attachment = forms.FileField(required=False)
    send_to_all = forms.BooleanField(initial=True, required=False)
    selected_users = forms.ModelMultipleChoiceField(
        queryset=CustomUser.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control'})
    )