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

    # Attendance URLs
    path('attendance/mark/', views.mark_attendance, name='mark_attendance'),

    # Leave Management URLs
    path('leaves/apply/', views.apply_leave, name='apply_leave'),
    path('leaves/history/', views.leave_history, name='leave_history'),

    # Payroll URLs
    path('payslip/', views.payslip, name='payslip'),
]