import os
from django.conf import settings
from scripts.ppt_generator import generate_presentation
from scripts.timesheet_validation import TimeValidator, OutputManager
from hr_management.models import PPTGenerationLog
from hr_management.models.timesheet import TimesheetEmailLog
from hr_management.repositories.user_repository import UserRepository
from common.email_utils import EmailSender

class AutomationService:
    @staticmethod
    def generate_ppt(user, data, excel_file=None):
        output_path = os.path.join(settings.MEDIA_ROOT, "Final_Anniversary_Presentation.pptx")
        
        excel_path = None
        if excel_file:
            excel_path = os.path.join(settings.MEDIA_ROOT, "uploaded.xlsx")
            with open(excel_path, "wb+") as destination:
                for chunk in excel_file.chunks():
                    destination.write(chunk)

        template_path = os.path.join(settings.MEDIA_ROOT, "WorkAnniversaryLogo.pptx")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        generate_presentation(
            template_path=template_path,
            excel_path=excel_path if excel_path else "dummy.xlsx",
            output_path=output_path,
            user_name=data["name"],
            years_of_service=data["years"],
        )

        PPTGenerationLog.objects.create(
            employee_name=data["name"],
            years_of_service=str(data["years"]),
            created_by=user,
        )
        return output_path

    @staticmethod
    def _setup_time_tracking_directories():
        timesheet_dir = os.path.join(settings.MEDIA_ROOT, "time_tracking")
        output_dir = os.path.join(settings.MEDIA_ROOT, "time_tracking_outputs")
        archive_dir = os.path.join(settings.MEDIA_ROOT, "time_tracking_archives")
        validation_dir = os.path.join(settings.MEDIA_ROOT, "time_tracking_validations")

        for directory in [timesheet_dir, output_dir, archive_dir, validation_dir]:
            os.makedirs(directory, exist_ok=True)
            
        return timesheet_dir, output_dir, archive_dir, validation_dir

    @staticmethod
    def process_time_tracking(timesheet_file, validation_type="standard"):
        timesheet_dir, output_dir, archive_dir, validation_dir = AutomationService._setup_time_tracking_directories()
        
        validator = TimeValidator()
        output_manager = OutputManager(output_dir, archive_dir, validation_dir)

        timesheet_path = os.path.join(timesheet_dir, timesheet_file.name)
        with open(timesheet_path, "wb+") as dest:
            for chunk in timesheet_file.chunks():
                dest.write(chunk)

        validation_result = validator.run(timesheet_path)

        if not validation_result["success"]:
            raise ValueError(validation_result.get("error", "Unknown error"))

        validated_sheets = {}
        for sheet_name, df in validation_result["validated_sheets"].items():
            processed_records = []
            for record in df.astype(str).to_dict(orient="records"):
                status = "Valid"
                flag = ""
                if "Status" in record and record["Status"] and record["Status"] not in ["OK", "Valid"]:
                    status = "Invalid"
                    flag = f"⚠ {record['Status']}"
                record["Status"] = status
                record["Flag"] = flag
                processed_records.append(record)
            validated_sheets[sheet_name] = processed_records

        summary_data = []
        summary_df = validation_result["summary"].astype(str)
        for record in summary_df.to_dict(orient="records"):
            status = "Valid"
            flag = ""
            if "Status" in record and record["Status"] and record["Status"] not in ["OK", "Valid"]:
                status = "Invalid"
                flag = f"⚠ {record['Status']}"
            record["Status"] = status
            record["Flag"] = flag
            summary_data.append(record)

        validation_number = 1 if validation_type == "custom" else None
        validated_file_path = output_manager.save_validated_data(validation_result, validation_number)
        
        if validated_file_path:
            output_manager.create_zip_archive(validated_file_path)

        return timesheet_file.name, validated_sheets, summary_data

    @staticmethod
    def generate_time_tracking_template(month, year, user_name):
        _, output_dir, archive_dir, validation_dir = AutomationService._setup_time_tracking_directories()
        output_manager = OutputManager(output_dir, archive_dir, validation_dir)
        template_path = output_manager.generate_monthly_template(month, year, user_name)
        if template_path and os.path.exists(template_path):
            return template_path
        raise ValueError("Failed to generate template")

    @staticmethod
    def send_time_tracking_email(sender, recipient_email, json_data):
        project = json_data.get("file_name", "Unknown File")
        recipient_user = UserRepository.get_by_email(recipient_email)
        
        email_sender = EmailSender()
        default_subject = f"Time Tracking Flags - {project}"

        try:
            success, flag_count = email_sender.send_flagged_data(
                recipient_email=recipient_email,
                subject=default_subject,
                json_data=json_data,
            )

            TimesheetEmailLog.objects.create(
                recipient=recipient_user,
                project_name=project,
                status="Success" if success else "Email sending failed without exception",
                email_content=json_data,
                sent_by=sender,
            )
            return success, flag_count
        except Exception as e:
            TimesheetEmailLog.objects.create(
                recipient=recipient_user,
                project_name=project,
                status=str(e),
                email_content=json_data,
                sent_by=sender,
            )
            raise e
