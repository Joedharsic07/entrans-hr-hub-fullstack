from django.utils import timezone
import datetime
from hr_management.repositories.attendance_repository import AttendanceRepository
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderServiceError

class AttendanceService:
    @staticmethod
    def get_logs(user):
        if user.is_staff:
            return AttendanceRepository.get_all_logs()
        return AttendanceRepository.get_user_logs(user)
    
    @staticmethod
    def get_geo_coordinates(lat, lng):
        geolocator = Nominatim(user_agent="attendance_app")
        try:
            location = geolocator.reverse((lat, lng), exactly_one=True)
            return location.address
        except Exception:
            return None

    @staticmethod
    def clock_in(user, lat, lng):
        today = datetime.date.today()
        log, created = AttendanceRepository.get_log_for_today(user, today)
        
        if log.clock_in:
            raise ValueError("Already punched in today.")
        
        now = timezone.now()
        log.clock_in = now
        
        if lat is not None and lng is not None:
            log.punch_in_latitude = lat
            log.punch_in_longitude = lng

        if now.hour > 9 or (now.hour == 9 and now.minute > 30):
            log.is_late_login = True
        
        if lat is not None and lng is not None:
            address = AttendanceService.get_geo_coordinates(lat, lng)
            if address:
                log.punch_in_address = address            
            
        log.save()
        return log

    @staticmethod
    def clock_out(user, lat, lng):
        today = datetime.date.today()
        log = AttendanceRepository.get_log_by_date(user, today)
        
        if not log:
            raise ValueError("No punch in record found for today.")
        
        now = timezone.now()
        log.clock_out = now
        
        if lat is not None and lng is not None:
            log.punch_out_latitude = lat
            log.punch_out_longitude = lng
            address = AttendanceService.get_geo_coordinates(lat, lng)
            if address:
                log.punch_out_address = address
        
        if log.clock_in:
            duration = now - log.clock_in
            hours = duration.total_seconds() / 3600
            
            if hours >= 8:
                log.attendance_status = "Present"
            elif hours >= 4:
                log.attendance_status = "Half Day"
            else:
                log.attendance_status = "Absent"
            
            if now.hour < 17:
                log.is_early_logout = True
                
        log.save()
        return log
