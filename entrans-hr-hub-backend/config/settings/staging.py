from .base import *

DEBUG = False

ALLOWED_HOSTS = [
    "staging.entrans-hr-hub.com",
    "entrans-hr-hub-staging.onrender.com",
    "*"
]

CSRF_TRUSTED_ORIGINS = [
    "https://staging.entrans-hr-hub.com",
    "https://entrans-hr-hub-staging.onrender.com",
]

# Database might use a different staging DB URL
if os.getenv("STAGING_DATABASE_URL"):
    DATABASES = {"default": dj_database_url.config(default=os.getenv("STAGING_DATABASE_URL"))}

FRONTEND_BASE_URL = os.getenv("FRONTEND_BASE_URL", "https://staging.entrans-hr-hub.vercel.app")

# Storage Configuration
# If using AWS S3 or other cloud storage, we would configure django-storages here.
# For now, we'll keep it using local media/storage mapping but explicitly defined.
MEDIA_ROOT = BASE_DIR / "storage"
MEDIA_URL = "/storage/"

# Security Settings for Staging
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
