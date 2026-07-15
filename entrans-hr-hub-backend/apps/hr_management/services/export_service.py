import csv
import io
import openpyxl
from reportlab.pdfgen import canvas
from hr_management.repositories.attendance_repository import AttendanceRepository
from hr_management.repositories.leave_repository import LeaveRepository

class ExportService:
    @staticmethod
    def export_attendance_excel(user):
        logs = AttendanceRepository.get_all_logs() if user.is_staff else AttendanceRepository.get_user_logs(user)
        
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Attendance"
        ws.append(["Employee", "Date", "Clock In", "Clock Out", "Total Hours", "Late Login", "Early Logout"])
        
        for log in logs:
            ws.append([
                log.employee.name,
                str(log.date),
                log.clock_in.strftime("%H:%M:%S") if log.clock_in else "",
                log.clock_out.strftime("%H:%M:%S") if log.clock_out else "",
                log.total_working_hours,
                "Yes" if log.is_late_login else "No",
                "Yes" if log.is_early_logout else "No"
            ])
        
        buffer = io.BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        return buffer

    @staticmethod
    def export_attendance_pdf(user):
        logs = AttendanceRepository.get_all_logs() if user.is_staff else AttendanceRepository.get_user_logs(user)
        
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer)
        p.drawString(100, 800, "Attendance Report")
        y = 750
        
        for log in logs:
            p.drawString(100, y, f"{log.employee.name} | {log.date} | {log.total_working_hours} hrs")
            y -= 20
            if y < 50:
                p.showPage()
                y = 800
        
        p.showPage()
        p.save()
        buffer.seek(0)
        return buffer

    @staticmethod
    def export_attendance_csv(user):
        logs = AttendanceRepository.get_all_logs() if user.is_staff else AttendanceRepository.get_user_logs(user)
        
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(["Employee", "Date", "Clock In", "Clock Out", "Total Hours", "Late Login", "Early Logout"])
        
        for log in logs:
            writer.writerow([
                log.employee.name,
                log.date,
                log.clock_in.strftime("%H:%M:%S") if log.clock_in else "",
                log.clock_out.strftime("%H:%M:%S") if log.clock_out else "",
                log.total_working_hours,
                log.is_late_login,
                log.is_early_logout
            ])
            
        buffer.seek(0)
        return buffer

    @staticmethod
    def export_leaves_csv(user):
        leaves = LeaveRepository.get_all_requests() if user.is_staff else LeaveRepository.get_user_requests(user)
        
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(["Employee", "Leave Type", "Start Date", "End Date", "Status"])
        
        for leave in leaves:
            writer.writerow([
                leave.employee.name,
                leave.leave_type,
                leave.start_date,
                leave.end_date,
                leave.status
            ])
            
        buffer.seek(0)
        return buffer
