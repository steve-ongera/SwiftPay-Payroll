from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserRegistrationForm
from .models import *
import logging
from django.utils.timezone import now
from django.db.models import Count
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model
from datetime import timedelta
from django.db.models import Sum
from .forms import *  # You'll create this form
from .models import (
    CustomUser, Department, EmployeeRole, 
    Attendance, Salary, PaySlip, 
    LeaveApplication
)
from .forms import (
    UserRegistrationForm, UserLoginForm, 
    EmployeeProfileForm,
    LeaveApplicationForm
)
import datetime
logger = logging.getLogger(__name__)


@login_required
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

    return render(request, 'employees/add_employee.html', {'form': form})

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
    today = timezone.now().date()
    total_employees = CustomUser.objects.count()
    total_departments = Department.objects.count()

    # Count employees on leave (Approved leaves with current date in range)
    employees_on_leave = LeaveApplication.objects.filter(
        status='APPROVED',
        start_date__lte=now().date(),
        end_date__gte=now().date()
    ).count()

    # Get latest payroll data
    latest_payroll = Salary.objects.order_by('-year', '-month').first()
    
    if latest_payroll:
        payroll_summary = Salary.objects.filter(
            month=latest_payroll.month,
            year=latest_payroll.year
        ).aggregate(
            total_net=Sum('net_salary')
        )
        payroll_amount = payroll_summary['total_net'] or 0
    else:
        payroll_amount = 0
        latest_payroll = None
    
    # For counting distinct employees present today (works with all databases)
    employees_present_today = Attendance.objects.filter(
        date=today
    ).values_list('employee', flat=True).distinct().count()
    
    # Calculate attendance percentage (with protection against division by zero)
    attendance_percentage = 0
    if total_employees > 0:
        attendance_percentage = round(
            (employees_present_today / total_employees) * 100, 
            2
        )
    
    context = {
        'total_employees': total_employees,
        'employees_on_leave': employees_on_leave,
        'total_departments': total_departments,
        # Payroll data
        'payroll_amount': payroll_amount,
        'latest_payroll': latest_payroll,
        'employees_present_today': employees_present_today,
        'departments': Department.objects.all(),
        'recent_leaves': LeaveApplication.objects.filter(status='PENDING')[:5],
        'user_attendance': Attendance.objects.filter(
            employee=request.user,
            date=today
        ).first(),
        'attendance_percentage': attendance_percentage
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
    
    return render(request, 'employees/register_employee.html', {'form': form})

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
    return render(request, 'employees/employee_list.html', context)

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
    return render(request, 'employees/employee_profile.html', context)


def update_employee(request, employee_id):
    employee = get_object_or_404(CustomUser, employee_id=employee_id)

    if request.method == 'POST':
        # If joined_date is not in POST data, use the existing value
        post_data = request.POST.copy()
        if not post_data.get('joined_date'):
            post_data['joined_date'] = employee.joined_date

        form = EmployeeUpdateForm(post_data, request.FILES, instance=employee)
        
        if form.is_valid():
            form.save()
            messages.success(request, "Employee details updated successfully!")
            return redirect('employee_profile', employee_id=employee.employee_id)
        else:
            print("Form Errors:", form.errors)
            messages.error(request, "Please correct the errors below.")
    else:
        form = EmployeeUpdateForm(instance=employee)

    return render(request, 'employees/update_employee.html', {'form': form, 'employee': employee})

def delete_employee(request, employee_id):
    employee = get_object_or_404(CustomUser, employee_id=employee_id)

    if request.method == "POST":
        employee.delete()
        messages.success(request, f'Employee {employee.first_name} {employee.last_name} has been deleted.')
        return redirect('employee_list')  # Redirect to employee list after deletion

    return render(request, 'employees/confirm_delete.html', {'employee': employee})


@login_required
def apply_leave(request):
    if request.method == 'POST':
        form = LeaveApplicationForm(request.POST)
        if form.is_valid():
            # Manually calculate days
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            
            # Calculate number of days (inclusive of start and end dates)
            days = (end_date - start_date).days + 1
            
            leave_application = form.save(commit=False)
            leave_application.employee = request.user
            leave_application.days = days  # Explicitly set days
            leave_application.save()

            messages.success(request, "Leave application submitted successfully!")
            return redirect('user_leave_history')
    else:
        form = LeaveApplicationForm()

    return render(request, 'apply_leave.html', {'form': form})



#mark attendance
@login_required
def mark_attendance_for_today(request):
    if request.method == 'POST':
        form = AttendanceApplicationForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            reason = form.cleaned_data.get('reason', '')

            # Create leave entries for each day in the range
            current_date = start_date
            while current_date <= end_date:
                # Check if attendance record already exists
                attendance, created = Attendance.objects.get_or_create(
                    employee=request.user,
                    date=current_date,
                    defaults={
                        'check_in': current_date,
                        'is_present': False,
                        'is_leave': True
                    }
                )

                # Update existing record if not created
                if not created:
                    attendance.is_leave = True
                    attendance.is_present = False
                    attendance.save()

                current_date += timedelta(days=1)

            messages.success(request, f"Attendance  applied successfully from {start_date} to {end_date}")
            return redirect('user_leave_history')  # Redirect to leave history page
    else:
        form = LeaveApplicationForm()

    return render(request, 'attendance_apply_leave.html', {'form': form})


@login_required
def user_leave_history(request):
    leave_applications = LeaveApplication.objects.filter(
        employee=request.user
    ).order_by('-applied_on')

    return render(request, 'employees/user_leave_history.html', {
        'leave_applications': leave_applications
    })


#list of all leaves applied 
def leave_application_list(request):
    leave_applications = LeaveApplication.objects.all()
    return render(request, 'leave_application_list.html', {'leave_applications': leave_applications})

def leave_application_detail(request, pk):
    leave_application = get_object_or_404(LeaveApplication, pk=pk)
    return render(request, 'leave_application_detail.html', {'leave_application': leave_application})

def update_leave_status(request, pk):
    leave_application = get_object_or_404(LeaveApplication, pk=pk)
    
    if request.method == "POST":
        new_status = request.POST.get('status')
        if new_status in ['PENDING', 'APPROVED', 'REJECTED']:
            leave_application.status = new_status
            leave_application.save()
    
    return redirect('leave_application_detail', pk=pk)

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

# list of attendances  for admin 
def attendance_list(request):
    attendances = Attendance.objects.all().order_by('-date')
    return render(request, 'attendance_list.html', {'attendances': attendances})


@login_required
def user_attendance_list(request):
    attendances = Attendance.objects.filter(employee=request.user).order_by('-date')
    return render(request, 'user_attendance_list.html', {'attendances': attendances})

#salary
@login_required
def salary_list(request):
    salaries = Salary.objects.filter(employee=request.user).order_by('-year', '-month')
    return render(request, 'salary_list.html', {'salaries': salaries})


from django.shortcuts import render
from mywebsite.models import Salary
from datetime import datetime

def admin_salary_list(request):
    # Get the latest month and year from the database
    latest_salary = Salary.objects.order_by('-year', '-month').first()
    latest_month = latest_salary.month if latest_salary else datetime.today().month
    latest_year = latest_salary.year if latest_salary else datetime.today().year

    # Get filter values from the request (default to latest)
    selected_month = request.GET.get('month', latest_month)
    selected_year = request.GET.get('year', latest_year)

    # Get salaries based on the selected month and year
    salaries = Salary.objects.filter(month=selected_month, year=selected_year).order_by('-year', '-month')

    # Pass months and years for dropdown filters
    months = list(range(1, 13))  # Months 1-12
    years = Salary.objects.values_list('year', flat=True).distinct().order_by('-year')

    return render(request, 'admin_salary_list.html', {
        'salaries': salaries,
        'months': months,
        'years': years,
        'selected_month': int(selected_month),
        'selected_year': int(selected_year),
    })



from .forms import SalaryForm

def add_salary(request):
    if request.method == "POST":
        form = SalaryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_salary_list')  # Redirect to the salary list page
    else:
        form = SalaryForm()
    
    return render(request, 'add_salary.html', {'form': form})

# views.py
from django.shortcuts import get_object_or_404
from .models import Salary
from .utils import render_to_pdf
from django.http import HttpResponse
from django.template.loader import render_to_string

def generate_payslip_pdf(request, salary_id):
    salary = get_object_or_404(Salary, id=salary_id)
    
    gross_salary = salary.base_salary + salary.bonus
    tax_amount = salary.deductions
    
    context = {
        'salary': salary,
        'gross_salary': gross_salary,
        'tax_amount': tax_amount,
        'company_name': 'SwiftPay',
        'company_address': 'Kenyatta Business Rd, Nairobi',
        'logo': 'img/logo.png',  # Make sure your logo is simple and small
    }
    
    # Use the new receipt template
    pdf = render_to_pdf('receipt_payslip.html', context)
    
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = f"payslip_{salary.employee.username}_{salary.month}_{salary.year}.pdf"
        content = f"inline; filename={filename}"
        response['Content-Disposition'] = content
        return response
    return HttpResponse("Error generating PDF", status=500)



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



# List all departments
def department_list(request):
    departments = Department.objects.all()
    return render(request, 'departments/department_list.html', {'departments': departments})

# View department details
def department_detail(request, pk):
    department = get_object_or_404(Department, pk=pk)
    return render(request, 'departments/department_detail.html', {'department': department})

# Create a new department
def department_create(request):
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('department_list')
    else:
        form = DepartmentForm()
    return render(request, 'departments/department_form.html', {'form': form})

# Update an existing department
def department_update(request, pk):
    department = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            form.save()
            return redirect('department_list')
    else:
        form = DepartmentForm(instance=department)
    return render(request, 'departments/department_form.html', {'form': form})


from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Sum, Count , Avg
from .models import Salary
from datetime import datetime
from django.http import HttpResponseBadRequest

@login_required
@permission_required('payroll.view_salary', raise_exception=True)
def monthly_payroll_report(request):
    # Default to current month/year if not specified
    current_year = datetime.now().year
    current_month = datetime.now().month
    
    # Get parameters from request
    year = int(request.GET.get('year', current_year))
    month = int(request.GET.get('month', current_month))
    pdf_format = request.GET.get('format') == 'pdf'
    
    # Validate month/year
    if not (1 <= month <= 12) or year < 2000 or year > current_year + 1:
        return HttpResponseBadRequest("Invalid month or year specified")
    
    # Main payroll aggregation
    payroll_data = Salary.objects.filter(
        year=year,
        month=month
    ).aggregate(
        total_base=Sum('base_salary'),
        total_bonus=Sum('bonus'),
        total_tax=Sum('deductions'),
        total_net=Sum('net_salary'),
        employee_count=Count('employee', distinct=True)
    )
    
    # Department breakdown
    department_data = Salary.objects.filter(
        year=year,
        month=month
    ).values(
        'employee__department__name'
    ).annotate(
        dept_total=Sum('net_salary'),
        dept_avg=Avg('net_salary'),
        employee_count=Count('employee')
    ).order_by('-dept_total')
    
    # Top earners
    top_earners = Salary.objects.filter(
        year=year,
        month=month
    ).select_related('employee').order_by('-net_salary')[:10]
    
    context = {
        'report_month': month,
        'report_year': year,
        'month_name': datetime(year, month, 1).strftime('%B'),
        'payroll_data': payroll_data,
        'department_data': department_data,
        'top_earners': top_earners,
        'available_years': range(2020, current_year + 1),
        'company_name': "SwiftPay",  # Add your company name
        'company_address': "Kenyatta Business Rd, Nairobi",  # Add your address
    }

    # Handle PDF generation
    if pdf_format:
        try:
            from django.template.loader import get_template
            from xhtml2pdf import pisa
            import os
            from django.conf import settings

            # Set PDF response headers
            response = HttpResponse(content_type='application/pdf')
            filename = f"payroll_report_{year}_{month}.pdf"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'

            # Add logo path to context
            context['logo_path'] = os.path.join(settings.STATIC_ROOT, 'img/logo.png')

            # Render PDF template
            template = get_template('reports/monthly_summary_pdf.html')
            html = template.render(context)

            # Create PDF
            pisa_status = pisa.CreatePDF(
                html,
                dest=response,
                encoding='UTF-8',
                link_callback=lambda uri, _: os.path.join(settings.STATIC_ROOT, uri.replace(settings.STATIC_URL, ''))
            )

            if pisa_status.err:
                return HttpResponse('PDF generation failed', status=500)
            return response

        except Exception as e:
            logger.error(f"PDF generation error: {str(e)}")
            return HttpResponse(f'PDF generation error: {str(e)}', status=500)

    return render(request, 'reports/monthly_summary.html', context)


# views.py
from django.shortcuts import get_object_or_404
from django.http import HttpResponseForbidden
from decimal import Decimal

@login_required
def employee_tax_certificate(request, employee_id=None, year=None):
    # Default to current user if no employee_id specified
    if employee_id is None:
        employee = request.user
    else:
        employee = get_object_or_404(CustomUser, pk=employee_id)
    
    # Default to previous year if not specified
    current_year = datetime.now().year
    report_year = int(year) if year else (current_year - 1)
    
    # Check permissions (users can only view their own unless they have permission)
    if employee != request.user and not request.user.has_perm('payroll.view_salary'):
        return HttpResponseForbidden("You don't have permission to view this report")
    
    # Get all salary records for the year
    salaries = Salary.objects.filter(
        employee=employee,
        year=report_year
    ).order_by('month')
    
    # Calculate YTD totals
    ytd_totals = salaries.aggregate(
        total_base=Sum('base_salary'),
        total_bonus=Sum('bonus'),
        total_tax=Sum('deductions'),
        total_net=Sum('net_salary')
    )
    
    # Calculate effective tax rate
    gross_income = (ytd_totals['total_base'] or Decimal('0')) + (ytd_totals['total_bonus'] or Decimal('0'))
    tax_paid = ytd_totals['total_tax'] or Decimal('0')
    effective_tax_rate = (tax_paid / gross_income * 100) if gross_income > 0 else 0
    
    context = {
        'employee': employee,
        'report_year': report_year,
        'salaries': salaries,
        'ytd_totals': ytd_totals,
        'gross_income': gross_income,
        'effective_tax_rate': round(effective_tax_rate, 2),
        'available_years': range(2020, current_year + 1),
    }
    
    # PDF response if requested
    if request.GET.get('format') == 'pdf':
        from .utils import render_to_pdf
        pdf = render_to_pdf('reports/tax_certificate_pdf.html', context)
        if pdf:
            filename = f"Tax_Certificate_{employee.username}_{report_year}.pdf"
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
    
    return render(request, 'reports/tax_certificate.html', context)


from django.template.loader import get_template
from xhtml2pdf import pisa
from django.conf import settings
import os

def generate_tax_certificate_pdf(request, context):
    template = get_template('reports/tax_certificate_pdf.html')
    html = template.render(context)
    
    # Handle logo path
    logo_path = os.path.join(settings.STATIC_ROOT, 'img/logo.png')
    context['logo_path'] = logo_path
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Tax_Certificate_{context["employee"].id}_{context["report_year"]}.pdf"'
    
    pisa_status = pisa.CreatePDF(
        html,
        dest=response,
        link_callback=lambda uri, _: os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, '')))
    
    return response