import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class EmailService:
    def __init__(self):
        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = int(settings.SMTP_PORT or 587)
        self.smtp_username = settings.SMTP_USERNAME
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.DEFAULT_FROM_EMAIL

    def _send(self, to_email: str, subject: str, html_body: str) -> bool:
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg.attach(MIMEText(html_body, 'html'))

            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.ehlo()
                server.starttls(context=context)
                server.login(self.smtp_username, self.smtp_password)
                server.sendmail(self.from_email, to_email, msg.as_string())

            logger.info(f"Email sent successfully to {to_email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False

    def send_welcome_email_with_temp_password(self, to_email: str, first_name: str, temp_password: str) -> bool:
        subject = "Welcome to HR Hub \u2013 Your Account Details"
        html = f"""
        <html>
        <body style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;padding:20px;">
          <div style="background:#1F3A5F;padding:20px;border-radius:8px 8px 0 0;">
            <h1 style="color:#fff;margin:0;">HR Hub</h1>
          </div>
          <div style="background:#f9f9f9;padding:30px;border:1px solid #ddd;border-radius:0 0 8px 8px;">
            <h2 style="color:#1F3A5F;">Welcome, {first_name}!</h2>
            <p>Your account has been created successfully. Here are your login credentials:</p>
            <div style="background:#fff;border:1px solid #e0e0e0;border-radius:6px;padding:20px;margin:20px 0;">
              <p><strong>Email:</strong> {to_email}</p>
              <p><strong>Temporary Password:</strong>
                <code style="background:#f0f0f0;padding:3px 8px;border-radius:4px;font-size:15px;">{temp_password}</code>
              </p>
            </div>
            <p style="color:#e53e3e;"><strong>Important:</strong> This temporary password expires in
            <strong>24 hours</strong>. Please log in and change your password immediately.</p>
            <hr style="border:none;border-top:1px solid #eee;margin:20px 0;">
            <p style="color:#888;font-size:12px;">This is an automated message. Please do not reply to this email.</p>
          </div>
        </body>
        </html>
        """
        return self._send(to_email, subject, html)

    def send_password_changed_email(self, to_email: str, first_name: str) -> bool:
        subject = "HR Hub \u2013 Password Changed Successfully"
        html = f"""
        <html>
        <body style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;padding:20px;">
          <div style="background:#1F3A5F;padding:20px;border-radius:8px 8px 0 0;">
            <h1 style="color:#fff;margin:0;">HR Hub</h1>
          </div>
          <div style="background:#f9f9f9;padding:30px;border:1px solid #ddd;border-radius:0 0 8px 8px;">
            <h2 style="color:#1F3A5F;">Hello, {first_name}!</h2>
            <p>Your password has been changed successfully.</p>
            <p>If you did not make this change, please contact your administrator immediately.</p>
            <hr style="border:none;border-top:1px solid #eee;margin:20px 0;">
            <p style="color:#888;font-size:12px;">This is an automated message. Please do not reply to this email.</p>
          </div>
        </body>
        </html>
        """
        return self._send(to_email, subject, html)

    def send_timesheet_reminder(
        self,
        to_email: str,
        first_name: str,
        missing_by_project: dict,   # { project_name: [date, ...] }
        period_start,
        period_end,
    ) -> bool:
        total_missing = sum(len(v) for v in missing_by_project.values())
        subject = (
            f"HR Hub \u2013 Timesheet Reminder: "
            f"{total_missing} Missing {'Day' if total_missing == 1 else 'Days'} "
            f"across {len(missing_by_project)} Project{'s' if len(missing_by_project) > 1 else ''}"
        )

        # Build per-project HTML blocks
        project_blocks_html = ''
        for project_name, days in missing_by_project.items():
            day_items = ''.join(
                f'<li style="padding:3px 0;color:#475569;">'
                f'{d.strftime("%A, %d %b %Y")}</li>'
                for d in sorted(days)
            )
            project_blocks_html += f"""
            <div style="margin-bottom:16px;">
              <p style="margin:0 0 6px;font-weight:bold;color:#1F3A5F;font-size:14px;">
                &#128193; {project_name}
                <span style="font-weight:normal;color:#94a3b8;font-size:12px;">
                  — {len(days)} missing {'day' if len(days) == 1 else 'days'}
                </span>
              </p>
              <ul style="margin:0;padding-left:20px;">{day_items}</ul>
            </div>
            """

        html = f"""
        <html>
        <body style="font-family:Arial,sans-serif;max-width:620px;margin:0 auto;padding:20px;">
          <div style="background:#1F3A5F;padding:20px;border-radius:8px 8px 0 0;">
            <h1 style="color:#fff;margin:0;">HR Hub</h1>
          </div>
          <div style="background:#f9f9f9;padding:30px;border:1px solid #ddd;border-radius:0 0 8px 8px;">
            <h2 style="color:#1F3A5F;margin-top:0;">Hello, {first_name}!</h2>
            <p>This is a reminder that you have
            <strong>{total_missing} unfilled timesheet
            {'entry' if total_missing == 1 else 'entries'}</strong>
            for the current salary period:</p>

            <p style="text-align:center;font-size:15px;font-weight:bold;
               background:#e0e7ff;border-radius:8px;padding:10px;color:#3730a3;">
              {period_start.strftime('%d %b %Y')} &nbsp;&rarr;&nbsp;
              {period_end.strftime('%d %b %Y')}
            </p>

            <div style="background:#fff;border:1px solid #e0e0e0;border-radius:6px;
                        padding:20px;margin:20px 0;">
              {project_blocks_html}
            </div>

            <p>Please log in to <strong>HR Hub</strong> and fill in the missing entries
            before the salary period closes on
            <strong>the 20th of the month</strong>.</p>

            <hr style="border:none;border-top:1px solid #eee;margin:20px 0;">
            <p style="color:#888;font-size:12px;">
              This is an automated reminder. Please do not reply to this email.
            </p>
          </div>
        </body>
        </html>
        """
        return self._send(to_email, subject, html)
