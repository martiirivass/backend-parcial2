from typing import Optional

from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    nombre: str
    email: EmailStr
    password: str
    tipo_documento_codigo: Optional[str] = None
    numero_documento: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RolInfo(BaseModel):
    codigo: str
    nombre: str


class RegisterResponse(BaseModel):
    id: int
    nombre: str
    email: str


class LoginResponse(BaseModel):
    message: str


class RefreshResponse(BaseModel):
    message: str


class LogoutResponse(BaseModel):
    message: str


class UserResponse(BaseModel):
    id: int
    nombre: str
    email: str
    tipo_documento_id: Optional[int] = None
    numero_documento: Optional[str] = None
    roles: list[RolInfo] = []


class MeResponse(UserResponse):
    pass
