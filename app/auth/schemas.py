from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    nombre: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RolInfo(BaseModel):
    id: int
    codigo: str
    nombre: str

class UserResponse(BaseModel):
    id: int
    nombre: str
    email: str
    roles: list[RolInfo] = []