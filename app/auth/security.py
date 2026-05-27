import hashlib
from datetime import datetime, timedelta, UTC

import jwt
from passlib.context import CryptContext


SECRET_KEY = "secret" #clave privada para firmar jwt
ALGORITHM = "HS256" #algoritmo criptografico de sha-456 para firmar jwt
ACCESS_TOKEN_EXPIRE_MINUTES = 30 #tiempo de expiracion de jwt

#configura como se manejan las contraseñas
pwd_context = CryptContext(
    schemes=["bcrypt"], #usa bcrypt para hash de contraseñas
    deprecated="auto",
    bcrypt__rounds=12 #define costo computacional
)

#convierte la contraseña en hash
def hash_password(password: str):
    return pwd_context.hash(password)

#compara la contraseña ingresada con el hash almacenado
def verify_password(
    plain_password: str,
    hashed_password: str
):
    return pwd_context.verify(
        plain_password,
        hashed_password
    )

#hashea el  refresh token
def hash_token(token: str) -> str:
    """SHA-256 del token para almacenar como CHAR(64)."""
    return hashlib.sha256(token.encode()).hexdigest() #string hexadecimal

#Crea el token con expiracion, contiene id del usuario
def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.now(UTC) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({
        "exp": expire
    })

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )