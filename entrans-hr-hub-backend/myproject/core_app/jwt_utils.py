import os
import uuid
from datetime import datetime, timedelta, timezone
from django.conf import settings
import jwt
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from uuid import uuid4
from datetime import datetime, timedelta
from django.conf import settings
import jwt
import logging

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Token lifetimes
# ---------------------------------------------------------------------------
ACCESS_TOKEN_MINUTES = 15
REFRESH_TOKEN_DAYS = 7


def _get_user(user_or_id):
    """Return a User instance from either a User object or a user ID."""
    User = get_user_model()
    if isinstance(user_or_id, (int, str)):
        try:
            return User.objects.get(id=user_or_id)
        except User.DoesNotExist:
            return None
    return user_or_id


def generate_token(user_or_id, token_type: str) -> str:
    """
    Generate a signed JWT token.

    Access tokens include the full user profile payload.
    Refresh tokens carry only the minimal identity claims (sub, jti, type).

    Parameters
    ----------
    user_or_id : User instance | int | str
        Either a Django User object or a user primary-key value.
    token_type : str
        'access' or 'refresh'
    """
    user = _get_user(user_or_id)
    user_id = user.id if user else int(user_or_id)

    now = datetime.utcnow()
    expiry = now + (
        timedelta(minutes=ACCESS_TOKEN_MINUTES)
        if token_type == 'access'
        else timedelta(days=REFRESH_TOKEN_DAYS)
    )

    # ── Core claims (always present) ─────────────────────────────────────
    payload = {
        'sub': str(user_id),
        'user_id': user_id,
        'token_type': token_type,
        'type': token_type,          # backward compat with existing code
        'jti': str(uuid4()),
        'iat': now,
        'exp': expiry,
        'iss': 'hr-hub-backend',
    }

    # ── Extended user claims (access tokens only) ─────────────────────────
    if token_type == 'access' and user is not None:
        is_admin = user.is_staff or user.is_superuser
        payload.update({
            'email': user.email,
            'user_name': user.name or '',
            'given_name': user.first_name or '',
            'name': f"{user.first_name or ''} {user.last_name or ''}".strip() or user.name or '',
            'user_role': 'Admin' if is_admin else 'User',
            'is_admin': is_admin,
            'designation': getattr(user, 'designation', '') or '',
            'is_active': user.is_active,
        })

    return jwt.encode(
        payload,
        settings.SIMPLE_JWT['SIGNING_KEY'],
        algorithm='HS256',
    )


def verify_token(token: str) -> dict:
    """
    Verify and decode a JWT token.

    Requires the core claims that are present in both access and refresh tokens.
    """
    payload = jwt.decode(
        token,
        settings.SIMPLE_JWT['SIGNING_KEY'],
        algorithms=['HS256'],
        options={
            'verify_exp': True,
            'require': ['sub', 'user_id', 'type', 'jti', 'exp', 'iat'],
        },
    )
    return payload


def get_user_from_token(token: str):
    """Return the Django User corresponding to the token's subject claim."""
    try:
        payload = verify_token(token)
        User = get_user_model()
        user_id = payload.get('sub') or payload.get('user_id')
        return User.objects.get(id=user_id)
    except Exception as e:
        raise Exception(f"Failed to get user from token: {str(e)}")


def refresh_token(refresh_token_str: str) -> str:
    """Issue a new access token from a valid refresh token."""
    payload = verify_token(refresh_token_str)
    if payload.get('type') != 'refresh':
        raise Exception("Invalid token type — refresh token required")
    user_id = payload.get('sub') or payload.get('user_id')
    return generate_token(user_id, 'access')
