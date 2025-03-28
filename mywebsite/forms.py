from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import RegexValidator
from .models import (
    CustomUser, Department, EmployeeRole, 
    Attendance, Salary, LeaveApplication, 
    LeaveType, TaxDeclaration
)

# forms.py
from django import forms
from .models import LeaveApplication, LeaveType
from django.utils import timezone
from datetime import timedelta
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

class LeaveApplicationForm(forms.ModelForm):
    leave_type = forms.ModelChoiceField(
        queryset=LeaveType.objects.all(), 
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text="Select the type of leave you're applying for"
    )
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        help_text="First day of your leave"
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        help_text="Last day of your leave"
    )
    reason = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        help_text="Provide a reason for your leave application"
    )

    class Meta:
        model = LeaveApplication
        fields = ['leave_type', 'start_date', 'end_date', 'reason']

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        leave_type = cleaned_data.get('leave_type')
        
        # Validate date range
        if start_date and end_date:
            if start_date > end_date:
                raise forms.ValidationError("End date must be after start date")
            
            # Calculate number of days
            days = (end_date - start_date).days + 1
            cleaned_data['days'] = days

            # Check leave type annual limit
            if leave_type:
                current_year = timezone.now().year
                existing_leaves = LeaveApplication.objects.filter(
                    employee=self.initial.get('employee'),
                    leave_type=leave_type,
                    start_date__year=current_year,
                    status__in=['PENDING', 'APPROVED']
                )
                
                total_days = sum(leave.days for leave in existing_leaves)
                total_days += days

                # Detailed error message
                if total_days > leave_type.max_days_per_year:
                    remaining_days = leave_type.max_days_per_year - (total_days - days)
                    error_message = (
                        f"You have exceeded the maximum allowed {leave_type.name} days. "
                        f"Maximum allowed: {leave_type.max_days_per_year} days, "
                        f"Already used/pending: {total_days - days} days, "
                        f"Remaining days: {remaining_days} days"
                    )
                    raise forms.ValidationError(error_message)

        return cleaned_data

# forms.py
from django import forms
from .models import Attendance, CustomUser
#attendance signing
class AttendanceApplicationForm(forms.ModelForm):
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        help_text="Start date of your todays job"
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        help_text="End date of your leave"
    )
    reason = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        required=False,
        help_text="Optional: Provide reason for leave"
    )

    class Meta:
        model = Attendance
        fields = ['start_date', 'end_date', 'reason']

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date:
            if start_date > end_date:
                raise forms.ValidationError("End date must be after start date")
        
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
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'middle_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'employee_id': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'joined_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-control'}),
            'is_active_employee': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'residential_status': forms.TextInput(attrs={'class': 'form-control'}),
            'national_id': forms.TextInput(attrs={'class': 'form-control'}),
            'kra_pin': forms.TextInput(attrs={'class': 'form-control'}),
            'nssf_no': forms.TextInput(attrs={'class': 'form-control'}),
            'nhif_no': forms.TextInput(attrs={'class': 'form-control'}),
            'passport_photo': forms.FileInput(attrs={'class': 'form-control'}),
            'basic_salary': forms.NumberInput(attrs={'class': 'form-control'}),
            'bank': forms.TextInput(attrs={'class': 'form-control'}),
            'bank_account_name': forms.TextInput(attrs={'class': 'form-control'}),
            'bank_account_number': forms.TextInput(attrs={'class': 'form-control'}),
            'bank_branch': forms.TextInput(attrs={'class': 'form-control'}),
            'employee_personal_number': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_employment': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'contract_type': forms.Select(attrs={'class': 'form-control'}),
            'job_title': forms.TextInput(attrs={'class': 'form-control'}),
            'employee_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'mobile_phone': forms.TextInput(attrs={'class': 'form-control'}),
        }


class EmployeeUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            'employee_id', 'middle_name', 'last_name', 'date_of_birth', 'gender', 'phone_number', 
            'address', 'joined_date', 'role', 'department', 'is_active_employee', 
            'residential_status', 'national_id', 'kra_pin', 'nssf_no', 'nhif_no', 
            'passport_photo', 'basic_salary', 'bank', 'bank_account_name', 'bank_account_number', 
            'bank_branch', 'employee_personal_number', 'date_of_employment', 'contract_type', 
            'job_title', 'employee_email', 'mobile_phone'
        ]

        widgets = {
            'employee_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'middle_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Middle Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Address'}),
            'joined_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'is_active_employee': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'residential_status': forms.Select(attrs={'class': 'form-select'}),
            'national_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'National ID'}),
            'kra_pin': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'KRA PIN'}),
            'nssf_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'NSSF Number'}),
            'nhif_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'NHIF Number'}),
            'passport_photo': forms.FileInput(attrs={'class': 'form-control'}),
            'basic_salary': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Basic Salary'}),
            'bank': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Bank Name'}),
            'bank_account_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Account Name'}),
            'bank_account_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Account Number'}),
            'bank_branch': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Bank Branch'}),
            'employee_personal_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Personal Number'}),
            'date_of_employment': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'contract_type': forms.Select(attrs={'class': 'form-select'}),
            'job_title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Job Title'}),
            'employee_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Employee Email'}),
            'mobile_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mobile Phone'}),
        }