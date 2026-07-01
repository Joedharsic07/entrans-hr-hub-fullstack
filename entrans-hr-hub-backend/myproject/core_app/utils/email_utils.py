import smtplib
import ssl
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from django.conf import settings
from collections import defaultdict

logger = logging.getLogger(__name__)

class EmailSender:
    def __init__(self):
        """Initialize email sender with SMTP settings"""
        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = int(settings.SMTP_PORT or 587)
        self.smtp_username = settings.SMTP_USERNAME
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.DEFAULT_FROM_EMAIL

    def prepare_email_content(self, json_data):
        """
        Prepare email content from flagged timesheet entries and missing dates
        Returns: (success_status, email_body)
        """
        validated_data = json_data.get('validated_data', {})
        raw_missing_dates = json_data.get('missing_dates', {})
        flagged_entries = []

        missing_dates = []
        if isinstance(raw_missing_dates, dict):
            for project_dict in raw_missing_dates.values():
                if isinstance(project_dict, dict):
                    for dates in project_dict.values():
                        missing_dates.extend(dates if isinstance(dates, list) else [dates])
        else:
            missing_dates = raw_missing_dates if isinstance(raw_missing_dates, list) else [raw_missing_dates]

        if isinstance(validated_data, dict):
            for sheet_entries in validated_data.values():
                flagged_entries.extend([
                    entry for entry in sheet_entries
                    if entry.get('Status') != 'Valid'
                ])
        elif isinstance(validated_data, list):
            flagged_entries = [
                entry for entry in validated_data
                if entry.get('Status') != 'Valid'
            ]

        if not flagged_entries and not missing_dates:
            return False, "No flagged entries or missing dates found"

        grouped_entries = defaultdict(list)
        for entry in flagged_entries:
            sheet = (
                entry.get("Project") or
                entry.get("ProjectName") or
                entry.get("project_name") or
                entry.get("Sheet") or
                "Unknown Sheet"
            )
            grouped_entries[sheet].append(entry)

        total_issues = len(flagged_entries) + len(missing_dates)
        email_body = (
            "Hello,\n\n"
            "The following issues were found in your timesheet submission:\n\n"
            f"Total Issues Found: {total_issues}\n\n"
        )

        for sheet, entries in grouped_entries.items():
            email_body += f"File name / Project - {sheet}:\n"
            email_body += "_" * 35 + "\n"
            for entry in entries:
                flag_message = entry.get("Flag", entry.get("Status", "Unknown Issue"))
                date = entry.get("Date", "N/A")
                description = entry.get("Description", "N/A")
                hours = entry.get("Hours", "N/A")

                email_body += f"Error/Warning: {flag_message}\n"
                email_body += "Related Timesheet Row:\n"
                email_body += f"  Date: {date}\n"
                email_body += f"  Description: {description}\n"
                email_body += f"  Hours: {hours}\n"
                email_body += "-" * 60 + "\n"
            email_body += "\n"

        if missing_dates:
            email_body += "Missing Timesheet Dates:\n"
            email_body += "-" * 35 + "\n"
            for missing_date in missing_dates:
                email_body += f"- {missing_date}\n"
            email_body += "-" * 60 + "\n\n"

        email_body += "Please review and correct the above entries as soon as possible.\n\n"
        return True, email_body
    
    def send_flagged_data(self, recipient_email, subject, json_data):
        """
        Send flagged timesheet data via email
        Returns: (success_status, number_of_flagged_entries)
        """
        success, email_body = self.prepare_email_content(json_data)
        if not success:
            return False, 0

        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"ACTION REQUIRED: {subject}"
            msg['From'] = self.from_email
            msg['To'] = recipient_email
            msg.attach(MIMEText(email_body, 'plain'))

            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.ehlo()
                server.starttls(context=context)
                server.ehlo()
                server.login(self.smtp_username, self.smtp_password)
                server.sendmail(self.from_email, [recipient_email], msg.as_string())

            logger.info(f"Flagged timesheet email sent to {recipient_email}")

            validated_data = json_data.get('validated_data', {})
            flagged_count = 0
            
            if isinstance(validated_data, dict):
                for sheet_entries in validated_data.values():
                    flagged_count += len([
                        entry for entry in sheet_entries
                        if entry.get('Status') != 'Valid'
                    ])
            elif isinstance(validated_data, list):
                flagged_count = len([
                    entry for entry in validated_data
                    if entry.get('Status') != 'Valid'
                ])

            return True, flagged_count

        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP authentication failed for {recipient_email}: {str(e)}")
            return False, 0
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error sending to {recipient_email}: {str(e)}")
            return False, 0
        except Exception as e:
            logger.error(f"Unexpected error sending email to {recipient_email}: {str(e)}")
            return False, 0
    
    def get_flag_count(self, json_data):
        """Helper method to count flagged entries"""
        validated_data = json_data.get('validated_data', {})
        if isinstance(validated_data, dict):
            return sum(
                len([entry for entry in entries if entry.get('Status') != 'Valid'])
                for entries in validated_data.values()
            )
        elif isinstance(validated_data, list):
            return len([
                entry for entry in validated_data
                if entry.get('Status') != 'Valid'
            ])
        return 0