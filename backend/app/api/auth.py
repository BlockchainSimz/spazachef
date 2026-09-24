"""Authentication endpoints backed by Supabase Auth."""
from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel, EmailStr, Field

from app.security.auth import (
    clear_session_cookies,
    refresh,
    set_session_cookies,
    sign_in,
    sign_up,
    current_user,
    REFRESH_COOKIE,
)
from fastapi import Cookie

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


class Credentials(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


@router.post("/register")
async def register(credentials: Credentials, response: Response) -> dict[str, object]:
    data = await sign_up(credentials.email, credentials.password)
    if not data.get("access_token"):
        return {"requires_email_confirmation": True}
    set_session_cookies(response, data)
    return {"user": data.get("user"), "authenticated": True}


@router.post("/login")
async def login(credentials: Credentials, response: Response) -> dict[str, object]:
    data = await sign_in(credentials.email, credentials.password)
    set_session_cookies(response, data)
    return {"user": data.get("user"), "authenticated": True}


@router.post("/refresh")
async def refresh_session(
    response: Response,
    refresh_token: str | None = Cookie(default=None, alias=REFRESH_COOKIE),
) -> dict[str, object]:
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh session required")
    data = await refresh(refresh_token)
    set_session_cookies(response, data)
    return {"user": data.get("user"), "authenticated": True}


@router.get("/me")
async def me(user: dict = __import__("fastapi").Depends(current_user)) -> dict[str, object]:
    return {"user": user, "authenticated": True}


@router.post("/logout")
async def logout(response: Response) -> dict[str, bool]:
    clear_session_cookies(response)
    return {"authenticated": False}
