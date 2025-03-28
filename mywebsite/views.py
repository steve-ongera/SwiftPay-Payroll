from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserRegistrationForm
from .models import *
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model
from .forms import EmployeeRegistrationForm  # You'll create this form
from .models import (
    CustomUser, Department, EmployeeRole, 
    Attendance, Salary, PaySlip, 
    LeaveApplication
)
from .forms import (
    UserRegistrationForm, UserLoginForm, 
    EmployeeProfileForm, AttendanceForm,
    LeaveApplicationForm
)
import datetime

def home(request):
    """
    Home page view
    """
    return render(request, 'home.html')

User = get_user_model()

def add_employee(request):
    if request.method == 'POST':
        form = EmployeeRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            employee = form.save(commit=False)
            employee.set_password('12345678')  # Set default password
            employee.save()
            messages.success(request, "Employee added successfully!")
            return redirect('employee_list')  # Change to your actual redirect path
    else:
        form = EmployeeRegistrationForm()

    return render(request, 'add_employee.html', {'form': form})

def register(request):
    if request.method == "POST":
        form = CustomUserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.password = make_password(form.cleaned_data["password"])  # Hash the password
            user.save()
            login(request, user)  # Auto-login after registration
            return redirect('user_dashboard')  # Redirect to the homepage (Change to your desired page)
    else:
        form = CustomUserRegistrationForm()
    
    return render(request, 'register.html', {'form': form})


def user_login(request):
    """
    User login view that redirects normal users to user_dashboard
    and superusers to admin_dashboard.
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful!')
            
            # Redirect based on user type
            if user.is_superuser:
                return redirect('dashboard')  # Redirect to admin dashboard
            else:
                return redirect('user_dashboard')  # Redirect to user dashboard
        else:
            messages.error(request, 'Invalid login credentials')

    return render(request, 'login.html')

@login_required
def dashboard(request):
    """
    Main dashboard view
    """
    context = {
        'total_employees': CustomUser.objects.count(),
        'departments': Department.objects.all(),
        'recent_leaves': LeaveApplication.objects.filter(status='PENDING')[:5],
        'user_attendance': Attendance.objects.filter(
            employee=request.user, 
            date=datetime.date.today()
        ).first()
    }
    
    return render(request, 'dashboard.html', context)


@login_required
def user_dashboard(request):
    """
    Display a summary of the logged-in user's information.
    """
    user = request.user

    context = {
        'employee': user,
        'attendance_records': Attendance.objects.filter(employee=user).order_by('-date')[:5],  # Last 5 attendance records
        'leave_applications': LeaveApplication.objects.filter(employee=user).order_by('-applied_on')[:5],  # Last 5 leave requests
        'salary_details': Salary.objects.filter(employee=user).order_by('-year', '-month')[:3],  # Last 3 salary records
        'payslips': PaySlip.objects.filter(salary__employee=user).order_by('-issue_date')[:3],  # Last 3 payslips
        'tax_declarations': TaxDeclaration.objects.filter(employee=user).order_by('-financial_year')[:2],  # Last 2 tax records
    }

    return render(request, 'user_dashboard.html', context)

@login_required
def logout_view(request):
    """
    User logout view
    """
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')

@login_required
def register_employee(request):
    """
    Employee registration view
    """
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, 'Employee registered successfully!')
            return redirect('employee_list')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'register_employee.html', {'form': form})

@login_required
def employee_list(request):
    """
    List all employees
    """
    employees = CustomUser.objects.all()
    
    # Optional filtering
    department = request.GET.get('department')
    role = request.GET.get('role')
    
    if department:
        employees = employees.filter(department__name=department)
    if role:
        employees = employees.filter(role__title=role)
    
    context = {
        'employees': employees,
        'departments': Department.objects.all(),
        'roles': EmployeeRole.objects.all()
    }
    return render(request, 'employee_list.html', context)

@login_required
def employee_profile(request, employee_id):
    """
    Employee profile view
    """
    employee = get_object_or_404(CustomUser, employee_id=employee_id)
    
    context = {
        'employee': employee,
        'attendance_records': Attendance.objects.filter(employee=employee)[:10],
        'salary_history': Salary.objects.filter(employee=employee),
        'leave_history': LeaveApplication.objects.filter(employee=employee)
    }
    return render(request, 'employee_profile.html', context)

@login_required
def mark_attendance(request):
    """
    Attendance marking view
    """
    if request.method == 'POST':
        form = AttendanceForm(request.POST)
        if form.is_valid():
            attendance = form.save(commit=False)
            attendance.employee = request.user
            attendance.date = datetime.date.today()
            attendance.check_in = datetime.datetime.now()
            attendance.save()
            messages.success(request, 'Attendance marked successfully!')
            return redirect('dashboard')
    else:
        # Check if attendance already marked today
        existing_attendance = Attendance.objects.filter(
            employee=request.user, 
            date=datetime.date.today()
        ).exists()
        
        if existing_attendance:
            messages.warning(request, 'Attendance already marked for today!')
            return redirect('dashboard')
        
        form = AttendanceForm()
    
    return render(request, 'mark_attendance.html', {'form': form})

def apply_leave(request):
    """
    View for employees to apply for leave
    """
    if request.method == 'POST':
        form = LeaveApplicationForm(request.POST)
        if form.is_valid():
            leave_application = form.save(commit=False)  # Save but don't commit
            leave_application.employee = request.user  # Assign the logged-in user
            leave_application.save()  # Now save to the database

            messages.success(request, "Leave application submitted successfully!")
            return redirect('leave_history')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = LeaveApplicationForm()

    return render(request, 'apply_leave.html', {'form': form})

@login_required
def leave_history(request):
    """
    Employee leave history view
    """
    leaves = LeaveApplication.objects.filter(employee=request.user)
    
    context = {
        'leaves': leaves
    }
    return render(request, 'leave_history.html', context)

@login_required
def payslip(request):
    """
    View to display payslips
    """
    # Get the latest salary record for the user
    latest_salary = Salary.objects.filter(employee=request.user).order_by('-id').first()
    
    context = {
        'salary': latest_salary
    }
    return render(request, 'payslip.html', context)