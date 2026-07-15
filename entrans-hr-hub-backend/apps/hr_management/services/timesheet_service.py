import pandas as pd
import calendar
from datetime import date, timedelta
from django.db.models import Sum, Case, When, Value, FloatField
from django.utils.dateparse import parse_date
from django.utils.timezone import is_naive, make_aware, get_current_timezone
from collections import defaultdict

from hr_management.repositories.timesheet_repository import TimesheetRepository
from hr_management.repositories.project_repository import UserProjectRepository, ProjectRepository
from hr_management.repositories.user_repository import UserRepository
from hr_management.models.timesheet import Timesheet, TimesheetEmailLog
from hr_management.models.automation import AutomationTimesheet, TimesheetType
from common.email_utils import EmailSender
from scripts.timesheet_validation import TimeValidator
from common.json_utils import convert_decimals, normalize_dict
from hr_management.serializers.timesheet import TimesheetSerializer
from hr_management.management.commands.send_timesheet_reminders import send_reminders

class TimesheetService:
    @staticmethod
    def get_timesheets(user, query_params):
        if user.is_staff or user.is_superuser:
            timesheets = TimesheetRepository.get_all_with_relations()
        else:
            user_projects = UserProjectRepository.get_user_projects(user)
            timesheets = TimesheetRepository.get_for_user_projects(user_projects)

        month_year = query_params.get("month_year")
        month = query_params.get("month")
        year = query_params.get("year")
        
        parsed_month = None
        parsed_year = None

        if month_year:
            try:
                parsed_month, parsed_year = map(int, month_year.split("/"))
                timesheets = TimesheetRepository.filter_by_month_year(timesheets, parsed_month, parsed_year)
            except (ValueError, AttributeError):
                pass
        elif month and year:
            try:
                parsed_month = int(month)
                parsed_year = int(year)
                timesheets = TimesheetRepository.filter_by_month_year(timesheets, parsed_month, parsed_year)
            except ValueError:
                pass

        if query_params.get("user_project") or query_params.get("user_project_id"):
            up_id = query_params.get("user_project") or query_params.get("user_project_id")
            timesheets = TimesheetRepository.filter_by_user_project(timesheets, up_id)
            
        if query_params.get("project_id"):
            timesheets = TimesheetRepository.filter_by_project(timesheets, query_params.get("project_id"))
            
        if query_params.get("work_type"):
            timesheets = TimesheetRepository.filter_by_work_type(timesheets, query_params.get("work_type"))

        return timesheets, parsed_month, parsed_year

    @staticmethod
    def calculate_statistics(timesheets):
        total_duration = timesheets.aggregate(total=Sum("duration"))["total"] or 0
        leave_days = (
            timesheets.annotate(
                leave_day_value=Case(
                    When(work_type="full_day_leave", then=Value(1.0)),
                    When(work_type="half_day_leave", then=Value(0.5)),
                    default=Value(0.0),
                    output_field=FloatField(),
                )
            ).aggregate(total=Sum("leave_day_value"))["total"]
            or 0.0
        )
        return total_duration, leave_days

    @staticmethod
    def validate_timesheet_data(raw_data):
        try:
            df = pd.DataFrame(raw_data)
            if not df.empty:
                df.rename(
                    columns={
                        "project_name": "Project",
                        "date": "Date",
                        "description": "Description",
                        "duration": "Hours",
                    },
                    inplace=True,
                )
                validator = TimeValidator()
                validated_df = validator.validate(df)
                validated_data = validated_df.astype(str).to_dict(orient="records")
                
                # Check if it has 'Sheet1' key needed for validator.create_summary
                summary_df = validator.create_summary({"Sheet1": validated_df})
                summary_data = summary_df.astype(str).to_dict(orient="records")
            else:
                validated_data = []
                summary_data = []
            return validated_data, summary_data, None
        except Exception as e:
            return [], [], str(e)

    @staticmethod
    def fill_missing_dates(raw_data, month, year):
        today = date.today()
        try:
            _, last_day = calendar.monthrange(year, month)
            start_date = date(year, month, 1)
            end_date = date(year, month, last_day)
            end_check_date = min(today, end_date)

            expected_dates = {
                (start_date + timedelta(days=i)).isoformat()
                for i in range((end_check_date - start_date).days + 1)
                if (start_date + timedelta(days=i)).weekday() < 5
            }

            existing_dates = {ts.get("date") for ts in raw_data}
            missing_dates = expected_dates - existing_dates

            for missed_date in sorted(missing_dates):
                raw_data.append(
                    {
                        "date": missed_date,
                        "duration": 0,
                        "work_type": "working",
                        "Status": f"You missed this date {missed_date}.Please fill in the timesheet",
                    }
                )
        except ValueError:
            pass
        return raw_data

    @staticmethod
    def get_timesheet_for_user(pk, user):
        timesheet = TimesheetRepository.get_by_id(pk)
        if timesheet and (timesheet.user_project.user == user or user.is_staff or user.is_superuser):
            return timesheet
        return None

    @staticmethod
    def delete_timesheet(pk, user):
        timesheet = TimesheetService.get_timesheet_for_user(pk, user)
        if not timesheet:
            raise ValueError("Timesheet not found or access denied")
        timesheet.delete()

    @staticmethod
    def get_user_timesheet_list(user):
        if user.is_staff:
            users = UserRepository.get_all_active()
            user_projects = UserProjectRepository.get_all().select_related("user", "project")
        else:
            users = [user]
            user_projects = UserProjectRepository.get_user_projects(user)

        response_data = []
        for u in users:
            user_data = {
                "user_id": u.id,
                "user_name": u.name,
                "user_email": u.email,
                "projects": [],
            }
            up_for_user = user_projects.filter(user=u)
            for up in up_for_user:
                project_data = {
                    "user_project_id": up.id,
                    "project_id": up.project.id,
                    "project_name": up.project.name,
                    "role": up.role,
                    "timesheets_link": f"user-timesheet/{up.id}/{up.project.id}",
                }
                user_data["projects"].append(project_data)
            response_data.append(user_data)
        
        return response_data

    @staticmethod
    def run_multiple_validations(user, month, year, user_project_map):
        validated_data = defaultdict(lambda: defaultdict(list))
        validation_summary = defaultdict(lambda: defaultdict(list))
        missing_dates = defaultdict(dict)
        total_duration = 0
        total_leave_days = 0
        errors = []
        first_timesheet_id = None

        month_date = date(year, month, 1)

        for uid, project_ids in user_project_map.items():
            for project_id in project_ids:
                try:
                    user_project_qs = UserProjectRepository.get_all().filter(user_id=uid, project_id=project_id)
                    if not user_project_qs.exists():
                        validated_data[uid][project_id] = []
                        missing_dates[uid][project_id] = []
                        validation_summary[uid][project_id].append(
                            {
                                "Status": "Invalid",
                                "Flag": "⚠ User not assigned to this project.",
                                "user_id": uid,
                                "project_id": project_id,
                            }
                        )
                        continue
                        
                    timesheets = Timesheet.objects.filter(
                        user_project__in=user_project_qs,
                        date__month=month,
                        date__year=year,
                    ).select_related("user_project__project")

                    if not timesheets.exists():
                        validation_summary[uid][project_id].append(
                            {
                                "Status": "Invalid",
                                "Flag": "⚠ No timesheets for this project.",
                                "user_id": uid,
                                "project_id": project_id,
                            }
                        )
                        continue

                    serializer = TimesheetSerializer(timesheets, many=True)
                    raw_data = serializer.data
                    
                    total_duration += sum(ts.duration for ts in timesheets)
                    leave_days = sum([
                        1.0 if ts.work_type == "full_day_leave" else 0.5 if ts.work_type == "half_day_leave" else 0.0
                        for ts in timesheets
                    ])
                    total_leave_days += leave_days

                    df = pd.DataFrame(raw_data)
                    if not df.empty:
                        df.rename(
                            columns={
                                "project_name": "Project",
                                "date": "Date",
                                "description": "Description",
                                "duration": "Hours",
                            },
                            inplace=True,
                        )

                        validator = TimeValidator()
                        result = validator.validate_dataframe(df)

                        if result["success"]:
                            enriched_validated = []
                            for validated_row, raw_row in zip(result["validated_data"], raw_data):
                                ts_id = raw_row.get("id")
                                validated_row["timesheet_id"] = ts_id
                                if not first_timesheet_id:
                                    first_timesheet_id = ts_id

                                status_text = validated_row.get("Status", "")
                                validated_row["Status"] = "Valid" if status_text in ["", "OK", "Valid"] else "Invalid"
                                validated_row["Flag"] = "" if validated_row["Status"] == "Valid" else f"⚠ {status_text}"
                                enriched_validated.append(validated_row)

                            validated_data[uid][project_id].extend(enriched_validated)

                            for summary in result.get("summary_data", []):
                                s_status = summary.get("Status", "")
                                summary["Status"] = "Valid" if s_status in ["", "OK", "Valid"] else "Invalid"
                                summary["Flag"] = "" if summary["Status"] == "Valid" else f"⚠ {s_status}"
                                validation_summary[uid][project_id].append(summary)
                        else:
                            errors.append({"user_id": uid, "project_id": project_id, "error": result["error"]})
                            continue

                    today = date.today()
                    _, last_day = calendar.monthrange(year, month)
                    start_date = date(year, month, 1)
                    end_date = date(year, month, last_day)
                    end_check_date = min(today, end_date)

                    expected_dates = {
                        (start_date + timedelta(days=i)).isoformat()
                        for i in range((end_check_date - start_date).days + 1)
                        if (start_date + timedelta(days=i)).weekday() < 5
                    }

                    existing_dates = {ts.get("date") for ts in raw_data}
                    missing = sorted(expected_dates - existing_dates)
                    missing_dates[uid][project_id] = missing

                except Exception as e:
                    errors.append({"user_id": uid, "project_id": project_id, "error": str(e)})
                    continue

        has_validations = any(bool(projects) for user_obj in validated_data.values() for projects in user_obj.values())
        
        if errors:
            overall_status = "Error"
        elif not has_validations:
            overall_status = "Needs to be run"
        else:
            overall_status = "Success"
            
        result_data = {
            "user_project_map": user_project_map,
            "validated_data": validated_data,
            "validation_summary": validation_summary,
            "statistics": {
                "total_duration": total_duration,
                "leave_days": total_leave_days,
            },
            "missing_dates": missing_dates,
            "errors": errors,
        }

        normalized_input = normalize_dict(user_project_map)
        existing_logs = AutomationTimesheet.objects.filter(month=month_date)
        timesheet_number = None
        existing_log = None

        for log in existing_logs:
            saved_map = log.result.get("user_project_map")
            if saved_map and normalize_dict(saved_map) == normalized_input:
                existing_log = log
                timesheet_number = log.timesheet_number
                break

        if existing_log:
            old_validated_data = convert_decimals(existing_log.result.get("validated_data", {}))
            new_validated_data = convert_decimals(validated_data)
            if normalize_dict(old_validated_data) != normalize_dict(new_validated_data):
                overall_status = "Needs rerun"

        if not existing_log:
            last_log = AutomationTimesheet.objects.order_by("-timesheet_number").first()
            timesheet_number = (last_log.timesheet_number if last_log else 0) + 1
            AutomationTimesheet.objects.create(
                timesheet_number=timesheet_number,
                type=TimesheetType.MANUAL,
                month=month_date,
                status=overall_status,
                result=convert_decimals(result_data),
            )
        else:
            existing_log.status = overall_status
            existing_log.result = convert_decimals(result_data)
            existing_log.save()
            
        result_data["status"] = overall_status
        return result_data

    @staticmethod
    def get_multiple_validation_status(user, month, year):
        month_date = date(year, month, 1)

        if user.is_staff:
            users = UserRepository.get_all_active()
            user_projects = UserProjectRepository.get_all().select_related("user", "project")
        else:
            users = [user]
            user_projects = UserProjectRepository.get_user_projects(user)

        response_data = []

        for u in users:
            user_data = {
                "user_id": u.id,
                "user_name": u.name,
                "user_email": u.email,
                "projects": [],
            }

            up_for_user = user_projects.filter(user=u)
            for up in up_for_user:
                project_id = up.project.id
                validation_logs = AutomationTimesheet.objects.filter(month=month_date).order_by("-updated_at")
                latest_log = None
                
                for log in validation_logs:
                    saved_map = log.result.get("user_project_map", {})
                    if str(u.id) in saved_map and project_id in saved_map[str(u.id)]:
                        latest_log = log
                        break

                validation_status = "Needs to be run"
                error_messages = ""
                timesheet_validations = []

                if latest_log:
                    validated_data = latest_log.result.get("validated_data", {})
                    user_key = str(u.id)
                    project_key = str(project_id)
                    user_projects_data = validated_data.get(user_key, {}).get(project_key, [])

                    actual_entries = Timesheet.objects.filter(
                        user_project=up, date__year=year, date__month=month
                    ).values("date", "updated_at")

                    updated_map = {e["date"]: e["updated_at"] for e in actual_entries}
                    actual_dates = set(updated_map.keys())

                    _, last_day = calendar.monthrange(year, month)
                    expected_dates = {
                        date(year, month, day)
                        for day in range(1, last_day + 1)
                        if date(year, month, day).weekday() < 5
                    }
                    missing_dates = expected_dates - actual_dates

                    error_flags = []
                    has_changes = False

                    log_time = getattr(latest_log, "updated_at", latest_log.created_at)
                    if is_naive(log_time):
                        log_time = make_aware(log_time, timezone=get_current_timezone())

                    for entry in user_projects_data:
                        entry_date = entry.get("Date") or entry.get("date")
                        entry_status = entry.get("Status")
                        flag = entry.get("Flag")
                        changed = False
                        
                        if entry_date:
                            entry_dt = parse_date(entry_date)
                            ts_updated = updated_map.get(entry_dt)
                            if ts_updated:
                                if is_naive(ts_updated):
                                    ts_updated = make_aware(ts_updated, timezone=get_current_timezone())
                                if ts_updated > log_time:
                                    changed = True
                                    has_changes = True

                        timesheet_validations.append({**entry, "changed": changed})
                        if entry_status == "Invalid" and flag:
                            error_flags.append(flag.strip())

                    if not user_projects_data:
                        summary = latest_log.result.get("validation_summary", {})
                        project_summaries = summary.get(user_key, {}).get(project_key, [])
                        for item in project_summaries:
                            if item.get("Status") == "Invalid" and "no timesheet" in item.get("Flag", "").lower():
                                timesheet_validations.append({"Flag": item["Flag"], "Status": item["Status"], "changed": False})
                                error_flags.append(item["Flag"])

                    if actual_entries:
                        for missing_date in sorted(missing_dates):
                            timesheet_validations.append({
                                "Date": missing_date.isoformat(),
                                "Status": "Invalid",
                                "Flag": "Missing timesheet entry",
                                "changed": False,
                            })
                        error_flags.append(f"Missing timesheet for {missing_date.isoformat()}")

                    if has_changes:
                        validation_status = "Needs rerun"
                    else:
                        validation_status = latest_log.result.get("status", "Success")

                    if error_flags:
                        error_messages = "\n".join(error_flags)

                project_data = {
                    "user_project_id": up.id,
                    "project_id": project_id,
                    "project_name": up.project.name,
                    "role": up.role,
                    "validation_status": validation_status,
                    "error": error_messages or None,
                    "timesheet_validations": timesheet_validations,
                }
                user_data["projects"].append(project_data)
            
            response_data.append(user_data)

        return response_data

    @staticmethod
    def send_timesheet_emails(user, month, year, user_project_map):
        month_date = date(year, month, 1)
        log = AutomationTimesheet.objects.filter(month=month_date, status="Success").order_by("-id").first()
        
        if not log:
            raise ValueError("No validation log found for given month.")

        full_result = log.result or {}
        validated_data = full_result.get("validated_data", {})
        if not validated_data:
            raise ValueError("No validated data found in the automation log.")

        email_sender = EmailSender()
        success_emails = []
        failed_emails = []

        for uid, project_ids in user_project_map.items():
            target_user = UserRepository.get_by_id(uid)
            if not target_user or not target_user.email:
                failed_emails.append(f"User ID {uid} has no valid email.")
                continue

            uid_str = str(uid)
            user_data = validated_data.get(uid_str, {})
            user_missing_data = full_result.get("missing_dates", {}).get(uid_str, {})

            for project_id in project_ids:
                project_id_str = str(project_id)
                sheet_data = user_data.get(project_id_str, [])
                missing_data = user_missing_data.get(project_id_str, [])

                if not sheet_data and not missing_data:
                    failed_emails.append(f"❌ No data found for User ID {uid}, Project ID {project_id}.")
                    continue

                json_data = {
                    "validated_data": sheet_data,
                    "missing_dates": missing_data,
                    "file_name": f"Project {project_id}",
                }

                flagged = [e for e in (sheet_data if isinstance(sheet_data, list) else []) if e.get("Status") != "Valid"]
                flat_missing = (
                    missing_data if isinstance(missing_data, list) else (
                        [d for dates in missing_data.values() for d in (dates if isinstance(dates, list) else [dates])]
                        if isinstance(missing_data, dict) else []
                    )
                )

                if not flagged and not flat_missing:
                    failed_emails.append(f"⚠️ {target_user.email} - No flagged entries or missing dates to send")
                    continue

                success, count = email_sender.send_flagged_data(
                    recipient_email=target_user.email,
                    subject=f"Time Tracking Flags - Project {project_id}",
                    json_data=json_data,
                )

                TimesheetEmailLog.objects.create(
                    recipient=target_user,
                    project_name=f"Project {project_id}",
                    status="Success" if success else "Failed",
                    email_content=json_data,
                    sent_by=user if user.is_authenticated else None,
                )

                if success:
                    success_emails.append(f"✅ {target_user.email} - {count} issues")
                else:
                    failed_emails.append(f"❌ {target_user.email} - SMTP send failed (check server logs for details)")

        return success_emails, failed_emails

    @staticmethod
    def trigger_reminders(dry_run=False):
        return send_reminders(dry_run=dry_run)
