from django.db.models import QuerySet
from hr_management.models.timesheet import Timesheet

class TimesheetRepository:
    @staticmethod
    def get_by_id(timesheet_id) -> Timesheet | None:
        try:
            return Timesheet.objects.get(id=timesheet_id)
        except Timesheet.DoesNotExist:
            return None

    @staticmethod
    def get_all_with_relations() -> QuerySet:
        return Timesheet.objects.all().select_related("user_project", "user_project__user", "user_project__project")

    @staticmethod
    def get_for_user_projects(user_projects) -> QuerySet:
        return Timesheet.objects.filter(user_project__in=user_projects).select_related("user_project", "user_project__user", "user_project__project")

    @staticmethod
    def filter_by_month_year(queryset, month: int, year: int) -> QuerySet:
        return queryset.filter(date__month=month, date__year=year)

    @staticmethod
    def filter_by_project(queryset, project_id) -> QuerySet:
        return queryset.filter(user_project__project_id=project_id)

    @staticmethod
    def filter_by_user_project(queryset, user_project_id) -> QuerySet:
        return queryset.filter(user_project_id=user_project_id)

    @staticmethod
    def filter_by_work_type(queryset, work_type: str) -> QuerySet:
        return queryset.filter(work_type=work_type)
