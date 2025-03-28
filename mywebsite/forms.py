from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import RegexValidator
from .models import (
    CustomUser, Department, EmployeeRole, 
    Attendance, Salary, LeaveApplication, 
    LeaveType, TaxDeclaration
)

class UserLoginForm(forms.Form):
    """
    Login form for users
    """
    username = forms.CharField(
        max_length=50, 
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Password'
        })
    )


from django import forms
from .models import CustomUser

class CustomUserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ['username', 'employee_id', 'email', 'date_of_birth', 'gender', 'phone_number', 'address', 'password', 'confirm_password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")

        return cleaned_data



class UserRegistrationForm(forms.ModelForm):
    """
    Employee registration form
    """
    # Phone number validation
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$', 
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Password'
        })
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Confirm Password'
        })
    )
    phone_number = forms.CharField(
        validators=[phone_regex],
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Phone Number'
        })
    )

    class Meta:
        model = CustomUser
        fields = [
            'username', 'email', 'first_name', 'last_name', 
            'phone_number', 'date_of_birth', 'gender', 
            'department', 'role', 'address'
        ]
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control', 
                'type': 'date'
            }),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean(self):
        """
        Validate password matching
        """
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError(
                "Password and Confirm Password do not match"
            )
        return cleaned_data

class EmployeeProfileForm(forms.ModelForm):
    """
    Form for updating employee profile
    """
    class Meta:
        model = CustomUser
        fields = [
            'first_name', 'last_name', 'email', 
            'phone_number', 'address', 'department', 'role'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'department': forms.Select(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
        }

class AttendanceForm(forms.ModelForm):
    """
    Attendance marking form
    """
    class Meta:
        model = Attendance
        fields = ['check_in', 'check_out', 'is_leave']
        widgets = {
            'check_in': forms.DateTimeInput(attrs={
                'class': 'form-control', 
                'type': 'datetime-local'
            }),
            'check_out': forms.DateTimeInput(attrs={
                'class': 'form-control', 
                'type': 'datetime-local'
            }),
        }

class LeaveApplicationForm(forms.ModelForm):
    """
    Leave application form
    """
    class Meta:
        model = LeaveApplication
        fields = ['leave_type', 'start_date', 'end_date', 'reason', 'days']
        widgets = {
            'leave_type': forms.Select(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'days': forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),  # Disable manual input
        }

    def clean(self):
        """
        Validate leave dates and calculate leave days
        """
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if start_date and end_date:
            if start_date > end_date:
                raise forms.ValidationError("End date must be after start date")
            
            # Auto-calculate the number of leave days
            cleaned_data['days'] = (end_date - start_date).days + 1
        
        return cleaned_data

class SalaryForm(forms.ModelForm):
    """
    Salary processing form
    """
    class Meta:
        model = Salary
        fields = [
            'base_salary', 'bonus', 'deductions', 
            'tax_rate', 'month', 'year'
        ]
        widgets = {
            'base_salary': forms.NumberInput(attrs={'class': 'form-control'}),
            'bonus': forms.NumberInput(attrs={'class': 'form-control'}),
            'deductions': forms.NumberInput(attrs={'class': 'form-control'}),
            'tax_rate': forms.NumberInput(attrs={'class': 'form-control'}),
            'month': forms.Select(attrs={'class': 'form-control'}),
            'year': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class TaxDeclarationForm(forms.ModelForm):
    """
    Tax declaration form
    """
    class Meta:
        model = TaxDeclaration
        fields = [
            'financial_year', 'total_investment', 
            'tax_exemption_claimed'
        ]
        widgets = {
            'financial_year': forms.NumberInput(attrs={'class': 'form-control'}),
            'total_investment': forms.NumberInput(attrs={'class': 'form-control'}),
            'tax_exemption_claimed': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class DepartmentForm(forms.ModelForm):
    """
    Department creation/edit form
    """
    class Meta:
        model = Department
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class EmployeeRoleForm(forms.ModelForm):
    """
    Employee role creation/edit form
    """
    class Meta:
        model = EmployeeRole
        fields = ['title', 'base_salary', 'department']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'base_salary': forms.NumberInput(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-control'}),
        }


from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

class EmployeeRegistrationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'username', 'first_name', 'middle_name', 'last_name', 'employee_id',
            'date_of_birth', 'gender', 'phone_number', 'address', 'joined_date',
            'role', 'department', 'is_active_employee', 'residential_status', 
            'national_id', 'kra_pin', 'nssf_no', 'nhif_no', 'passport_photo',
            'basic_salary', 'bank', 'bank_account_name', 'bank_account_number',
            'bank_branch', 'employee_personal_number', 'date_of_employment', 
            'contract_type', 'job_title', 'employee_email', 'mobile_phone'
        ]

        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'joined_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'date_of_employment': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
