from django.db.models import Q
from hr_management.models.user import User
from hr_management.models.project import Project
from hr_management.models.leave import LeaveRequest

class SearchService:
    @staticmethod
    def global_search(query):
        results = []

        if not query:
            return results

        employees = User.objects.filter(
            Q(name__icontains=query) | Q(email__icontains=query)
        )[:5]
        for emp in employees:
            results.append({
                "type": "employee",
                "id": emp.id,
                "title": emp.name,
                "subtitle": emp.designation or "Employee"
            })

        projects = Project.objects.filter(name__icontains=query)[:5]
        for proj in projects:
            results.append({
                "type": "project",
                "id": proj.id,
                "title": proj.name,
                "subtitle": "Project"
            })

        leaves = LeaveRequest.objects.filter(employee__name__icontains=query)[:5]
        for leave in leaves:
            results.append({
                "type": "leave",
                "id": leave.id,
                "title": f"Leave Request - {leave.employee.name}",
                "subtitle": f"{leave.leave_type} ({leave.start_date})"
            })

        return results
