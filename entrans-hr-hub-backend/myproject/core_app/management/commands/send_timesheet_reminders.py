"""
Management command: send_timesheet_reminders

Salary period: 20th of the previous month → 20th of the current month.
The cron runs on the 18th at 18:00 as a reminder 2 days before the deadline.

Validation logic:
  - For every active user assigned to at least one project
  - For EACH project they belong to individually
  - Check every working day (Mon–Fri) in the salary period
  - If any day is missing a timesheet entry for that specific project → flag it
  - Send ONE consolidated email per user listing missing days grouped by project
  - Skips users who are fully up to date across all projects

Cron schedule (settings.py CRONJOBS): '0 18 18 * *'
Can also be triggered manually:
    python manage.py send_timesheet_reminders [--dry-run]
"""
import logging
from datetime import date, timedelta

from django.core.management.base import BaseCommand

from core_app.models import Timesheet, User, UserProject
from core_app.utils.email_service import EmailService

logger = logging.getLogger(__name__)


def get_salary_period(reference_date: date = None):
    """
    Return (period_start, period_end) for the salary period.

    Rule: 20th of the previous month → 20th of the current month.
    period_end is capped at today so we never flag future dates.

    Examples (cron runs on the 18th):
      Today = Jul 18 → period = Jun 20 → Jul 18  (cap; deadline Jul 20)
      Today = Jul 20 → period = Jun 20 → Jul 20  (full period closed)
      Today = Aug  5 → period = Jul 20 → Aug  5  (new period started)
    """
    today = reference_date or date.today()

    # Period always starts on the 20th of the *previous* month
    if today.day >= 20:
        period_start = date(today.year, today.month, 20)
        # Deadline is the 20th of *next* month
        if today.month == 12:
            period_end_deadline = date(today.year + 1, 1, 20)
        else:
            period_end_deadline = date(today.year, today.month + 1, 20)
    else:
        if today.month == 1:
            period_start = date(today.year - 1, 12, 20)
        else:
            period_start = date(today.year, today.month - 1, 20)
        # Deadline is the 20th of the current month
        period_end_deadline = date(today.year, today.month, 20)

    # Never include future dates in the check
    period_end = min(period_end_deadline, today)
    return period_start, period_end


def get_working_days(start: date, end: date):
    """Return all Mon–Fri dates between start and end (inclusive)."""
    days = []
    current = start
    while current <= end:
        if current.weekday() < 5:
            days.append(current)
        current += timedelta(days=1)
    return days


def send_reminders(dry_run: bool = False):
    """
    Core logic — called by the management Command and the API trigger view.

    For each active user → for each of their projects → find missing working days.
    One consolidated reminder email is sent per user listing all gaps by project.

    Returns a summary dict.
    """
    period_start, period_end = get_salary_period()
    working_days = get_working_days(period_start, period_end)

    logger.info(
        f"Reminder run | period: {period_start} → {period_end} "
        f"| {len(working_days)} working day(s) | dry_run={dry_run}"
    )

    if not working_days:
        logger.info("No working days in salary period — skipping.")
        return {
            "period_start": str(period_start),
            "period_end": str(period_end),
            "working_days": 0,
            "emails_sent": 0,
            "emails_skipped": 0,
            "emails_failed": 0,
        }

    email_service = EmailService()
    sent = skipped = failed = 0

    # All active users who are assigned to at least one project
    users = (
        User.objects
        .filter(is_active=True, userproject__isnull=False)
        .distinct()
    )

    for user in users:
        user_projects = (
            UserProject.objects
            .filter(user=user)
            .select_related('project')
        )

        # ── Per-project missing-day analysis ──────────────────────────────
        missing_by_project: dict[str, list[date]] = {}

        for up in user_projects:
            # Dates the user HAS submitted for this specific project
            filled_dates = set(
                Timesheet.objects
                .filter(
                    user_project=up,
                    date__gte=period_start,
                    date__lte=period_end,
                )
                .exclude(work_type__in=['weekend', 'holiday'])
                .values_list('date', flat=True)
            )

            missing = [d for d in working_days if d not in filled_dates]
            if missing:
                missing_by_project[up.project.name] = sorted(missing)

        if not missing_by_project:
            skipped += 1
            logger.debug(f"{user.email} — fully up to date, skipping.")
            continue

        total_missing = sum(len(v) for v in missing_by_project.values())
        logger.info(
            f"Reminder → {user.email}: "
            f"{total_missing} missing entry(ies) across "
            f"{len(missing_by_project)} project(s)"
        )

        if dry_run:
            sent += 1
            continue

        first_name = user.first_name or (user.name.split()[0] if user.name else user.email)

        success = email_service.send_timesheet_reminder(
            to_email=user.email,
            first_name=first_name,
            missing_by_project=missing_by_project,
            period_start=period_start,
            period_end=period_end,
        )

        if success:
            sent += 1
        else:
            failed += 1
            logger.error(f"Failed to send reminder to {user.email}")

    logger.info(
        f"Reminder run complete — sent={sent}, skipped={skipped}, failed={failed}"
    )
    return {
        "period_start": str(period_start),
        "period_end": str(period_end),
        "working_days": len(working_days),
        "emails_sent": sent,
        "emails_skipped": skipped,
        "emails_failed": failed,
    }


class Command(BaseCommand):
    help = (
        "Send timesheet reminder emails for the current salary period "
        "(20th prev-month → 20th current-month). "
        "Checks each user across each project individually. "
        "Scheduled automatically on the 18th at 18:00 via django-crontab."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Log which emails would be sent without actually sending.',
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        self.stdout.write("Starting timesheet reminder run...")
        result = send_reminders(dry_run=dry_run)
        self.stdout.write(self.style.SUCCESS(
            f"Done — sent={result['emails_sent']}, "
            f"skipped={result['emails_skipped']}, "
            f"failed={result['emails_failed']} | "
            f"Period: {result['period_start']} → {result['period_end']} "
            f"({result['working_days']} working days)"
        ))

class Command(BaseCommand):
    help = (
        "Send timesheet reminder emails to users with missing entries in the "
        "current salary period (20th prev-month → 19th current-month). "
        "Scheduled automatically on the 18th of each month at 18:00."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Log what would be sent without actually sending emails.',
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        self.stdout.write("Starting timesheet reminder run...")
        result = send_reminders(dry_run=dry_run)
        self.stdout.write(self.style.SUCCESS(
            f"Done — sent={result['emails_sent']}, "
            f"skipped={result['emails_skipped']}, "
            f"failed={result['emails_failed']} | "
            f"Period: {result['period_start']} → {result['period_end']}"
        ))
