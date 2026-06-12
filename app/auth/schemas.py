from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    nombre: str
    email: EmailStr
    password: str


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
    roles: list[RolInfo] = []


class MeResponse(UserResponse):
    pass
