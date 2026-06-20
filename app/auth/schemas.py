from typing import Optional
from datetime import datetime

from pydantic import BaseModel, EmailStr, field_validator


class RegisterRequest(BaseModel):
    nombre: str
    apellido: Optional[str] = ""
    email: EmailStr
    password: str
    tipo_documento_codigo: Optional[str] = None
    numero_documento: Optional[str] = None

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres")
        return v

    @field_validator("nombre")
    @classmethod
    def nombre_min_length(cls, v: str) -> str:
        if len(v) < 2:
            raise ValueError("El nombre debe tener al menos 2 caracteres")
        if len(v) > 80:
            raise ValueError("El nombre no puede superar los 80 caracteres")
        return v

    @field_validator("apellido")
    @classmethod
    def apellido_min_length(cls, v: str) -> str:
        if v and len(v) < 2:
            raise ValueError("El apellido debe tener al menos 2 caracteres")
        if v and len(v) > 80:
            raise ValueError("El apellido no puede superar los 80 caracteres")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres")
        return v


class RolInfo(BaseModel):
    codigo: str
    nombre: str


class RegisterResponse(BaseModel):
    id: int
    nombre: str
    apellido: str
    email: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class LoginResponse(BaseModel):
    message: str


class RefreshResponse(BaseModel):
    message: str


class LogoutResponse(BaseModel):
    message: str


class UserResponse(BaseModel):
    id: int
    nombre: str
    apellido: str
    email: str
    tipo_documento_id: Optional[int] = None
    numero_documento: Optional[str] = None
    created_at: Optional[datetime] = None
    roles: list[RolInfo] = []


class MeResponse(UserResponse):
    access_token: str | None = None
