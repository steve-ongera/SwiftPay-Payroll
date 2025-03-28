from django.contrib import admin
from .models import (
    Department, EmployeeRole, CustomUser, Attendance, LeaveType, 
    LeaveApplication, Salary, PaySlip, TaxDeclaration
)

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(EmployeeRole)
class EmployeeRoleAdmin(admin.ModelAdmin):
    list_display = ('title', 'base_salary', 'department')
    search_fields = ('title',)
    list_filter = ('department',)

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'employee_id', 'role', 'department', 'is_active_employee')
    search_fields = ('username', 'employee_id')
    list_filter = ('department', 'role', 'is_active_employee')

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'check_in', 'check_out', 'is_present', 'is_leave')
    search_fields = ('employee__username', 'date')
    list_filter = ('is_present', 'is_leave')

@admin.register(LeaveType)
class LeaveTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'max_days_per_year')

@admin.register(LeaveApplication)
class LeaveApplicationAdmin(admin.ModelAdmin):
    list_display = ('employee', 'leave_type', 'start_date', 'end_date', 'status')
    list_filter = ('status', 'leave_type')
    search_fields = ('employee__username',)

@admin.register(Salary)
class SalaryAdmin(admin.ModelAdmin):
    list_display = ('employee', 'month', 'year', 'net_salary')
    search_fields = ('employee__username', 'month', 'year')

@admin.register(PaySlip)
class PaySlipAdmin(admin.ModelAdmin):
    list_display = ('salary', 'issue_date', 'receipt_number', 'total_working_days', 'days_present')
    search_fields = ('salary__employee__username', 'receipt_number')

@admin.register(TaxDeclaration)
class TaxDeclarationAdmin(admin.ModelAdmin):
    list_display = ('employee', 'financial_year', 'total_investment', 'tax_exemption_claimed', 'is_verified')
    list_filter = ('financial_year', 'is_verified')
    search_fields = ('employee__username',)

