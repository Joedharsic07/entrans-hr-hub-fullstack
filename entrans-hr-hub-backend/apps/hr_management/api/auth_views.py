import logging
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import AllowAny
from hr_management.serializers.auth import MyTokenObtainPairSerializer, RegisterSerializer, LoginSerializer
from hr_management.serializers.user import UserSerializer
from hr_management.services.auth_service import AuthService
from common.jwt_utils import get_user_from_request

logger = logging.getLogger(__name__)

def _get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {
                    "status": "error",
                    "code": "invalid_input",
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = serializer.save()

            return Response(
                {
                    "status": "success",
                    "message": "User registered successfully. Please log in to continue.",
                    "user": UserSerializer(user).data,
                },
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            return Response(
                {
                    "status": "error",
                    "code": "server_error",
                    "message": "Internal server error during registration",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {
                    "status": "error",
                    "code": "invalid_input",
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            email = serializer.validated_data["email"]
            password = serializer.validated_data["password"]
            ip_address = _get_client_ip(request)
            user_agent = request.META.get("HTTP_USER_AGENT", "")

            result = AuthService.login(request, email, password, ip_address, user_agent)
            
            if result["status"] == "error":
                status_code = status.HTTP_401_UNAUTHORIZED
                if result.get("code") == "account_inactive":
                    status_code = status.HTTP_403_FORBIDDEN
                elif result.get("code") == "user_not_found":
                    status_code = status.HTTP_404_NOT_FOUND
                return Response(result, status=status_code)

            return Response(
                {
                    "status": "success",
                    "user": UserSerializer(result["user"]).data,
                    "access_token": result["access_token"],
                    "refresh_token": result["refresh_token"],
                }
            )

        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return Response(
                {
                    "status": "error",
                    "code": "server_error",
                    "message": "Internal server error",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

class GoogleLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        credential = request.data.get("credential")
        if not credential:
            return Response(
                {"status": "error", "message": "No Google credential provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            ip_address = _get_client_ip(request)
            user_agent = request.META.get("HTTP_USER_AGENT", "")
            result = AuthService.google_login(credential, ip_address, user_agent)

            if result["status"] == "error":
                status_code = status.HTTP_404_NOT_FOUND
                if result.get("code") == "account_inactive":
                    status_code = status.HTTP_403_FORBIDDEN
                return Response(result, status=status_code)

            return Response(
                {
                    "status": "success",
                    "user": UserSerializer(result["user"]).data,
                    "access_token": result["access_token"],
                    "refresh_token": result["refresh_token"],
                }
            )

        except ValueError:
            return Response(
                {"status": "error", "code": "invalid_token", "message": "Invalid Google token"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        except Exception as e:
            logger.error(f"Google login error: {str(e)}")
            return Response(
                {"status": "error", "code": "server_error", "message": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

class RefreshTokenView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.data.get("refresh_token")

        if not refresh_token:
            return Response(
                {"error": "Refresh token is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            access_token = AuthService.refresh_token(refresh_token)
            return Response({"access_token": access_token})
        except ValueError as ve:
            return Response(
                {"error": str(ve)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            logger.error(f"Refresh token error: {str(e)}")
            return Response(
                {"error": "Invalid refresh token"}, status=status.HTTP_401_UNAUTHORIZED
            )

class RequestPasswordResetView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response(
                {"status": "error", "message": "Email is required"}, status=400
            )

        try:
            result = AuthService.request_password_reset(email)
            if result["status"] == "error":
                if result.get("message") == "User not found":
                    return Response(result, status=404)
                return Response(result, status=500)
            return Response(result)
        except Exception as e:
            logger.error(f"[RESET_EMAIL_ERROR] {str(e)}")
            return Response(
                {"status": "error", "message": f"Failed to send email: {str(e)}"},
                status=500,
            )

class ConfirmPasswordResetView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get("token")
        new_password = request.data.get("new_password")

        if not token or not new_password:
            return Response(
                {"status": "error", "message": "Token and new password are required"},
                status=400,
            )

        try:
            result = AuthService.confirm_password_reset(token, new_password)
            if result.get("status") == "error":
                return Response(result, status=404)
            return Response({"status": "success", "message": "Password has been reset successfully"})
        except ValueError as e:
            return Response({"status": "error", "message": str(e)}, status=400)

class ChangePasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        user = get_user_from_request(request)
        if not user:
            return Response(
                {"error": "Authentication required"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        old_password = request.data.get("old_password", "")
        new_password = request.data.get("new_password", "")

        if not old_password or not new_password:
            return Response(
                {"error": "old_password and new_password are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            result = AuthService.change_password(user, old_password, new_password)
            if result["status"] == "error":
                return Response({"error": result["message"]}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"status": "success", "message": "Password changed successfully"})
        except Exception as e:
            logger.error(f"Change password error: {str(e)}")
            return Response(
                {"error": "Failed to change password"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
