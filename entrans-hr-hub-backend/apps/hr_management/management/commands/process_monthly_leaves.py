import logging
from datetime import date
from django.core.management.base import BaseCommand
from hr_management.models.user import User
from hr_management.models.leave import LeaveType, LeaveBalance
from django.db import transaction

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = (
        "Add 1 Sick Leave and 1 Earned Leave to all active users every month. "
        "Sick leave resets on January 1st to 1 day. Earned leave carries forward."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--force-january',
            action='store_true',
            help='Force the script to run as if it is January (resets Sick Leave).',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Log what would happen without actually modifying the database.',
        )

    def handle(self, *args, **options):
        force_jan = options.get('force_january', False)
        dry_run = options.get('dry_run', False)
        
        is_january = force_jan or (date.today().month == 1)

        self.stdout.write(f"Starting monthly leave processing... (is_january={is_january}, dry_run={dry_run})")
        
        active_users = User.objects.filter(is_active=True)
        users_processed = 0

        with transaction.atomic():
            for user in active_users:
                # Process Sick Leave
                sick_balance, _ = LeaveBalance.objects.get_or_create(
                    employee=user,
                    leave_type=LeaveType.SICK,
                    defaults={'total_days': 0.0, 'used_days': 0.0}
                )

                if is_january:
                    # Reset sick leave for the new year
                    if not dry_run:
                        sick_balance.total_days = 1.0
                        sick_balance.used_days = 0.0
                        sick_balance.save()
                    self.stdout.write(f"[{user.email}] Reset Sick Leave to 1.0 (Happy New Year!)")
                else:
                    if not dry_run:
                        sick_balance.total_days = float(sick_balance.total_days) + 1.0
                        sick_balance.save()
                    self.stdout.write(f"[{user.email}] Added 1.0 Sick Leave (Total: {float(sick_balance.total_days) + (1.0 if dry_run else 0.0)})")

                # Process Earned Leave
                earned_balance, _ = LeaveBalance.objects.get_or_create(
                    employee=user,
                    leave_type=LeaveType.EARNED,
                    defaults={'total_days': 0.0, 'used_days': 0.0}
                )
                
                if not dry_run:
                    earned_balance.total_days = float(earned_balance.total_days) + 1.0
                    earned_balance.save()
                
                self.stdout.write(f"[{user.email}] Added 1.0 Earned Leave (Total: {float(earned_balance.total_days) + (1.0 if dry_run else 0.0)})")
                users_processed += 1

        if dry_run:
            self.stdout.write(self.style.SUCCESS(f"[DRY-RUN] Would have processed leaves for {users_processed} users."))
        else:
            self.stdout.write(self.style.SUCCESS(f"Successfully processed leaves for {users_processed} users."))
