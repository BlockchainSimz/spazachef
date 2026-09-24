"""Supabase Auth integration and request authentication."""
from __future__ import annotations

from typing import Any

import httpx
from fastapi import Cookie, Header, HTTPException, status

from app.config import settings

ACCESS_COOKIE = "spazachef_access_token"
REFRESH_COOKIE = "spazachef_refresh_token"


def _require_supabase() -> str:
    if not settings.SUPABASE_URL or not settings.SUPABASE_ANON_KEY:
        raise HTTPException(status_code=503, detail="Authentication is not configured")
    return settings.SUPABASE_URL.rstrip("/")


def _headers() -> dict[str, str]:
    return {"apikey": settings.SUPABASE_ANON_KEY, "Content-Type": "application/json"}


async def _supabase_auth(path: str, payload: dict[str, Any]) -> dict[str, Any]:
    base = _require_supabase()
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(f"{base}/auth/v1/{path}", headers=_headers(), json=payload)
    if response.status_code >= 400:
        detail = "Authentication request failed"
        try:
            body = response.json()
            detail = str(body.get("msg") or body.get("message") or body.get("error_description") or detail)
        except ValueError:
            pass
        raise HTTPException(status_code=401, detail=detail)
    return response.json()


async def sign_up(email: str, password: str) -> dict[str, Any]:
    return await _supabase_auth("signup", {"email": email, "password": password})


async def sign_in(email: str, password: str) -> dict[str, Any]:
    return await _supabase_auth("token?grant_type=password", {"email": email, "password": password})


async def refresh(refresh_token: str) -> dict[str, Any]:
    return await _supabase_auth("token?grant_type=refresh_token", {"refresh_token": refresh_token})


async def get_user(access_token: str) -> dict[str, Any]:
    base = _require_supabase()
    headers = {**_headers(), "Authorization": f"Bearer {access_token}"}
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(f"{base}/auth/v1/user", headers=headers)
    if response.status_code >= 400:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired session")
    return response.json()


def _cookie_options() -> dict[str, Any]:
    return {
        "httponly": True,
        "secure": settings.is_production,
        "samesite": "lax",
        "path": "/",
        "max_age": settings.JWT_EXPIRATION_HOURS * 3600,
    }


def set_session_cookies(response: Any, auth_data: dict[str, Any]) -> None:
    access = auth_data.get("access_token")
    refresh_token = auth_data.get("refresh_token")
    if not access or not refresh_token:
        return
    options = _cookie_options()
    response.set_cookie(ACCESS_COOKIE, access, **options)
    response.set_cookie(
        REFRESH_COOKIE,
        refresh_token,
        httponly=True,
        secure=settings.is_production,
        samesite="lax",
        path="/",
        max_age=60 * 60 * 24 * 30,
    )


def clear_session_cookies(response: Any) -> None:
    response.delete_cookie(ACCESS_COOKIE, path="/")
    response.delete_cookie(REFRESH_COOKIE, path="/")


async def current_user(
    access_cookie: str | None = Cookie(default=None, alias=ACCESS_COOKIE),
    authorization: str | None = Header(default=None),
) -> dict[str, Any]:
    token = access_cookie
    if not token and authorization and authorization.lower().startswith("bearer "):
        token = authorization[7:].strip()
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    return await get_user(token)
