from django.contrib import admin
from .models import AutomationTimesheet, MonthChoices, TimesheetEmailLog, User, Project, UserProject,  Timesheet, HolidayWeekend
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin    
from django.utils.html import format_html
import json
import datetime 

@admin.register(User)
class UserAdmin(BaseUserAdmin):  
    list_display = ('id', 'name', 'email', 'is_staff')
    search_fields = ('name', 'email')
    list_filter = ('is_staff', 'is_active')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('name',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'password1', 'password2'),
        }),
    )

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'owner')
    search_fields = ('name',)
    list_filter = ('owner',)

@admin.register(UserProject)
class UserProjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'project', 'role')
    list_filter = ('user', 'project', 'role')
    search_fields = ('user__name', 'project__name')

@admin.register(Timesheet)
class TimesheetAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_project', 'date', 'task_name', 'duration', 'work_type','updated_at')
    list_filter = ('work_type', 'date', 'user_project__user', 'user_project__project')
    search_fields = ('task_name', 'user_project__user__name', 'user_project__project__name')

@admin.register(HolidayWeekend)
class HolidayWeekendAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'description')
    list_filter = ('date',)
    search_fields = ('description',)

@admin.register(AutomationTimesheet)
class AutomationTimesheetAdmin(admin.ModelAdmin):
    list_display = (
        'timesheet_number',
        'get_month_display',
        'type',
        'status',
        'created_at',
        'validation_summary',
    )
    list_filter = ('month', 'type', 'status', 'created_at')
    search_fields = ('timesheet_number',)
    readonly_fields = ('result_pretty',)

    def get_month_display(self, obj):
        value = obj.month
        if isinstance(value, datetime.date):
            value = value.strftime("%m") 
        try:
            return MonthChoices(value).label
        except ValueError:
            return value  

    def validation_summary(self, obj):
        try:
            result = obj.result or {}
            file_errors = result.get("file_errors", [])
            row_results = result.get("row_results", [])
            invalid_rows = [r for r in row_results if not r.get("valid", True)]
            return f"{len(file_errors)} file errors, {len(invalid_rows)} invalid rows"
        except Exception:
            return "Invalid JSON"
    validation_summary.short_description = 'Validation Summary'

    def result_pretty(self, obj):
        try:
            return format_html("<pre>{}</pre>", json.dumps(obj.result, indent=2))
        except Exception:
            return "Invalid JSON"
    result_pretty.short_description = "Validation Result"

@admin.register(TimesheetEmailLog)
class TimesheetEmailLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipient', 'project_name', 'status', 'sent_at', 'sent_by')
    list_filter = ('status', 'sent_at', 'sent_by')
    search_fields = ('project_name', 'recipient__username', 'recipient__email', 'sent_by__username', 'sent_by__email')
    readonly_fields = ('sent_at',)
    ordering = ('-sent_at',)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False