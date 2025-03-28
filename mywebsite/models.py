from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

class Allowance(models.Model):
    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name


class Department(models.Model):
    """
    Department model to categorize employees
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.name

class EmployeeRole(models.Model):
    """
    Roles for different employee positions
    """
    title = models.CharField(max_length=100)
    base_salary = models.DecimalField(max_digits=10, decimal_places=2)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    
    def __str__(self):
        return self.title

class CustomUser(AbstractUser):
    """
    Extended user model for employees
    """
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other')
    ]
    
    employee_id = models.CharField(max_length=20, unique=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    joined_date = models.DateField(default=timezone.now)
    role = models.ForeignKey(EmployeeRole, on_delete=models.SET_NULL, null=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    is_active_employee = models.BooleanField(default=True)

    middle_name = models.CharField(max_length=255, null=True, blank=True)
    residential_status = models.CharField(max_length=2, choices=[
        ('R', 'Resident'),
        ('NR', 'Non-Resident')
    ], null=True, blank=True)
    national_id = models.CharField(max_length=10, null=True, blank=True)
    kra_pin = models.CharField(max_length=11, null=True, blank=True)
    nssf_no = models.CharField(max_length=15, null=True, blank=True)
    nhif_no = models.CharField(max_length=15, null=True, blank=True)
    passport_photo = models.ImageField(upload_to='employee_photos/', blank=True, null=True)
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    bank = models.CharField(max_length=50, null=True, blank=True)
    bank_account_name = models.CharField(max_length=255, null=True, blank=True)
    bank_account_number = models.CharField(max_length=35, null=True, blank=True)
    bank_branch = models.CharField(max_length=40, null=True, blank=True)
    employee_personal_number = models.CharField(max_length=50, null=True, blank=True)
    date_of_employment = models.DateField(null=True, blank=True)
    contract_type = models.CharField(choices=[
        ('P', 'Permanent'),
        ('T', 'Temporary')
    ], max_length=1, null=True, blank=True)
    job_title = models.CharField(max_length=50, null=True, blank=True)
    employee_email = models.EmailField(null=True, blank=True)
    mobile_phone = models.CharField(max_length=15, null=True, blank=True)

    
    def __str__(self):
        return f"{self.username} - {self.employee_id}"

class Attendance(models.Model):
    """
    Employee attendance tracking
    """
    employee = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    date = models.DateField()
    check_in = models.DateTimeField()
    check_out = models.DateTimeField(null=True, blank=True)
    is_present = models.BooleanField(default=False)
    is_leave = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('employee', 'date')
    
    def __str__(self):
        return f"{self.employee.username} - {self.date}"

class LeaveType(models.Model):
    """
    Types of leaves available
    """
    name = models.CharField(max_length=50)
    max_days_per_year = models.IntegerField()
    
    def __str__(self):
        return self.name

class LeaveApplication(models.Model):
    """
    Employee leave applications
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected')
    ]
    
    employee = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    days = models.IntegerField()
    reason = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    applied_on = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.employee.username} - {self.leave_type.name}"

class Salary(models.Model):
    """
    Salary details and calculations
    """
    employee = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    base_salary = models.DecimalField(max_digits=10, decimal_places=2)
    bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    net_salary = models.DecimalField(max_digits=10, decimal_places=2)
    month = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)])
    year = models.IntegerField()
    
    def __str__(self):
        return f"{self.employee.username} - {self.month}/{self.year}"

class PaySlip(models.Model):
    """
    Monthly payslip generation
    """
    salary = models.OneToOneField(Salary, on_delete=models.CASCADE)
    issue_date = models.DateField()
    receipt_number = models.CharField(max_length=50, unique=True)
    total_working_days = models.IntegerField()
    days_present = models.IntegerField()
    
    def __str__(self):
        return f"Payslip-{self.receipt_number}"

class TaxDeclaration(models.Model):
    """
    Employee tax declarations and investments
    """
    employee = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    financial_year = models.IntegerField()
    total_investment = models.DecimalField(max_digits=10, decimal_places=2)
    tax_exemption_claimed = models.DecimalField(max_digits=10, decimal_places=2)
    submitted_date = models.DateField()
    is_verified = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.employee.username} - {self.financial_year}"