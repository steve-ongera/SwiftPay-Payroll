from django.urls import path
from . import views

urlpatterns = [
    # Authentication URLs
    path('', views.home, name='home'),
    path('login/', views.user_login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),

    # Dashboard URL
    path('dashboard/', views.dashboard, name='dashboard'),
    path('user_dashboard/', views.user_dashboard, name='user_dashboard'),

    # Employee Management URLs
    path('employees/', views.employee_list, name='employee_list'),
    path('employee/add/', views.add_employee, name='add_employee'),
    path('employees/register/', views.register_employee, name='register_employee'),
    path('employees/profile/<str:employee_id>/', views.employee_profile, name='employee_profile'),
    path('update-employee/<str:employee_id>/', views.update_employee, name='update_employee'),
    path('employee/delete/<str:employee_id>/', views.delete_employee, name='employee_delete'),

    # Attendance URLs
    path('attendance/mark/', views.mark_attendance_for_today, name='mark_attendance'),
    path('attendance/', views.attendance_list, name='attendance_list'),
    path('my-attendance/', views.user_attendance_list, name='user_attendance_list'),

    # Leave Management URLs
    path('leaves/apply/', views.apply_leave, name='apply_leave'),
    path('leaves/history/', views.leave_history, name='leave_history'),
    path('User/leaves/history/', views.user_leave_history, name='user_leave_history'),
    #admin leaves list
    path('leave-applications/', views.leave_application_list, name='leave_application_list'),
    path('leave-applications/<int:pk>/', views.leave_application_detail, name='leave_application_detail'),
    path('leave-applications/<int:pk>/update-status/', views.update_leave_status, name='update_leave_status'),

    # Payroll URLs
    path('payslip/', views.payslip, name='payslip'),
    path('my-salary/', views.salary_list, name='salary_list'),
    path('general-salaries/', views.admin_salary_list, name='admin_salary_list'),
    path('salary/add/', views.add_salary, name='add_salary'),
    path('payslip/<int:salary_id>/pdf/', views.generate_payslip_pdf, name='generate_payslip_pdf'),

    path('departments/', views.department_list, name='department_list'),
    path('departments/add/', views.department_create, name='department_create'),
    path('departments/<int:pk>/', views.department_detail, name='department_detail'),
    path('departments/<int:pk>/edit/', views.department_update, name='department_update'),

    path('reports/monthly/', views.monthly_payroll_report, name='monthly_payroll_report'),
    path('reports/tax-certificate/', views.employee_tax_certificate, name='tax_certificate'),
    path('reports/tax-certificate/<int:year>/', views.employee_tax_certificate, name='tax_certificate_year'),
    path('reports/tax-certificate/<int:employee_id>/<int:year>/', views.employee_tax_certificate, name='tax_certificate_full'),
]