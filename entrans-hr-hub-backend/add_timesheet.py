import os
import django
import sys
from datetime import date, timedelta

# Make sure we're in the right directory to load settings
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

# pyrefly: ignore [missing-import]
from hr_management.models import User, UserProject, Timesheet, Project

email = "[EMAIL_ADDRESS]"
try:
    user = User.objects.get(email=email)
except User.DoesNotExist:
    print(f"User {email} not found")
    exit(1)

# Find or create a UserProject
user_projects = UserProject.objects.filter(user=user)
if not user_projects.exists():
    print(f"No projects found for {email}, creating a dummy one...")
    project, _ = Project.objects.get_or_create(name="Default Project", owner=user, description="Dummy")
    up, _ = UserProject.objects.get_or_create(user=user, project=project, role="owner")
else:
    up = user_projects.first()

print(f"Using UserProject: {up}")

# June 1 to June 30, 2026
start_date = date(2026, 6, 1)
end_date = date(2026, 6, 30)
delta = timedelta(days=1)

current_date = start_date
created_count = 0
while current_date <= end_date:
    # weekday() returns 0 for Monday, 6 for Sunday
    if current_date.weekday() < 5:  # Monday to Friday
        ts, created = Timesheet.objects.get_or_create(
            user_project=up,
            date=current_date,
            defaults={
                'task_name': 'Development Tasks',
                'description': 'Worked on backend and frontend features',
                'duration': 8.0,
                'work_type': 'working'
            }
        )
        if created:
            created_count += 1
            print(f"Created timesheet for {current_date}")
        else:
            print(f"Timesheet already exists for {current_date}")
    current_date += delta

print(f"Done! Created {created_count} timesheet entries for June 2026.")
