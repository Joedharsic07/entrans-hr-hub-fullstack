import jwt
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth import authenticate
from django.utils.timezone import now
from rest_framework_simplejwt.tokens import RefreshToken
from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as google_auth_requests
from hr_management.repositories.user_repository import UserRepository
from common.jwt_utils import generate_token, verify_token
import smtplib
from email.mime.text import MIMEText
import logging

logger = logging.getLogger(__name__)

class AuthService:
    @staticmethod
    def generate_password_reset_token(user_id):
        payload = {
            "user_id": user_id,
            "type": "password_reset",
            "exp": datetime.utcnow() + timedelta(hours=1),
            "iat": datetime.utcnow(),
        }
        return jwt.encode(payload, settings.SIMPLE_JWT["SIGNING_KEY"], algorithm="HS256")

    @staticmethod
    def verify_password_reset_token(token):
        try:
            payload = jwt.decode(
                token, settings.SIMPLE_JWT["SIGNING_KEY"], algorithms=["HS256"]
            )
            if payload.get("type") != "password_reset":
                raise jwt.InvalidTokenError("Incorrect token type")
            return payload["user_id"]
        except (jwt.ExpiredSignatureError, jwt.DecodeError, jwt.InvalidTokenError) as e:
            logger.error(f"Invalid password reset token: {str(e)}")
            raise ValueError("Invalid or expired token")

    @staticmethod
    def login(request, email, password, ip_address, user_agent):
        user = authenticate(
            request,
            email=email,
            password=password,
            backend="hr_management.auth.EmailAuthBackend",
        )

        if user is None:
            db_user = UserRepository.get_by_email(email)
            if db_user:
                if not db_user.is_active:
                    return {"status": "error", "code": "account_inactive", "message": "Account is inactive"}
                
                UserRepository.log_access(db_user, "login", "failed", ip_address, user_agent)
                return {"status": "error", "code": "invalid_credentials", "message": "Invalid password"}
            
            return {"status": "error", "code": "user_not_found", "message": "No user with this email exists"}
        
        if user.password_expires_at and user.password_expires_at < now():
            return {"status": "error", "code": "password_expired", "message": "Your temporary password has expired. Please contact your administrator."}

        access_token = generate_token(user, "access")
        refresh_token = generate_token(user, "refresh")

        UserRepository.log_access(user, "login", "success", ip_address, user_agent)

        return {
            "status": "success",
            "user": user,
            "access_token": access_token,
            "refresh_token": refresh_token,
        }

    @staticmethod
    def google_login(credential, ip_address, user_agent):
        client_id = settings.GOOGLE_CLIENT_ID
        idinfo = google_id_token.verify_oauth2_token(
            credential, google_auth_requests.Request(), client_id
        )

        email = idinfo.get("email")
        if not email:
            raise ValueError("Email not found in Google token")
        
        user = UserRepository.get_by_email(email)
        if not user:
            return {"status": "error", "code": "user_not_found", "message": "No account found for this Google email. Please contact your administrator."}
        
        if not user.is_active:
            return {"status": "error", "code": "account_inactive", "message": "Account is inactive"}

        access_token = generate_token(user, "access")
        refresh_token = generate_token(user, "refresh")

        UserRepository.log_access(user, "login", "success", ip_address, user_agent)

        return {
            "status": "success",
            "user": user,
            "access_token": access_token,
            "refresh_token": refresh_token,
        }
    
    @staticmethod
    def refresh_token(refresh_token_str):
        try:
            payload = verify_token(refresh_token_str)
            if payload.get("type") != "refresh":
                raise ValueError("Invalid token type - not a refresh token")
            
            user_id = payload.get("sub", payload.get("user_id"))
            if not user_id:
                raise ValueError("Invalid token - no user ID")
            
            access_token = generate_token(user_id, "access")
            return access_token
        except Exception as custom_error:
            try:
                refresh = RefreshToken(refresh_token_str)
                return str(refresh.access_token)
            except Exception:
                raise custom_error
    
    @staticmethod
    def request_password_reset(email):
        user = UserRepository.get_by_email(email)
        if not user:
            return {"status": "error", "message": "User not found"}
        
        token = AuthService.generate_password_reset_token(user.id)
        reset_url = f"{settings.FRONTEND_BASE_URL}/reset-password?token={token}"
        email_body = f"""
        Hello {user.name or user.email},

        You requested a password reset. Please click the link below to reset your password:
        {reset_url}

        This link will expire in 1 hour.

        If you didn't request this, you can ignore this email.

        """

        msg = MIMEText(email_body)
        msg["Subject"] = "Password Reset Instructions"
        msg["From"] = settings.DEFAULT_FROM_EMAIL
        msg["To"] = user.email

        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.sendmail(
                settings.DEFAULT_FROM_EMAIL, [user.email], msg.as_string()
            )
        
        return {"status": "success", "reset_token": token}
    
    @staticmethod
    def confirm_password_reset(token, new_password):
        user_id = AuthService.verify_password_reset_token(token)
        user = UserRepository.get_by_id(user_id)
        if not user:
            return {"status": "error", "message": "User not found"}
        
        user.set_password(new_password)
        user.save()
        return {"status": "success"}
    
    @staticmethod
    def change_password(user, old_password, new_password):
        if not user.check_password(old_password):
            return {"status": "error", "message": "Current password is incorrect"}
        
        if len(new_password) < 8:
            return {"status": "error", "message": "New password must be at least 8 characters"}
        
        user.set_password(new_password)
        user.password_expires_at = None
        user.password_changed_at = now()
        user.save()

        from common.email_service import EmailService
        display_name = user.first_name or (
            user.name.split()[0] if user.name else user.email
        )
        EmailService().send_password_changed_email(user.email, display_name)

        return {"status": "success"}
