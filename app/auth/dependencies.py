from typing import Annotated

import jwt
from fastapi import Cookie, Depends, HTTPException
from sqlmodel import Session

#Importa la clave secreta del JWT, y el algoritmo de cifrado
from app.auth.security import (
    SECRET_KEY,
    ALGORITHM
)

from app.db.database import get_session
from app.models.usuario import Usuario

#funcion para buscar cookies, en caso de que haya, decodifica el jwt por si expiró
#Si no expiró, revisa que el usuario este registrado

def get_current_user(
    access_token: Annotated[ #esto le dice a fastapi:
                            #Busca una cookie llamada access_token
        str | None,
        Cookie()
    ] = None, # por defecto es None
    session: Session = Depends(get_session)  # conecta con la base de datos
):
    if not access_token:
        raise HTTPException(
            status_code=401,
            detail="No autenticado" #Si no trae cookie, tira el 401
        )

    #Verifica que el token haya sido firmado por el servidor (Secret_Key)
    #Y que no haya expirado.
    #Si esta todo bien trae a user_id
    #Si no un 401 con token invalido
    try:
        payload = jwt.decode(
            access_token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        user_id = payload.get("sub")

    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Token inválido"
        )
        
    #Codigo que pregunta : El usuario existe en la base de datos?
    user = session.get(
        Usuario,
        int(user_id)
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Usuario no encontrado" #Si no existe 401 No encontrado
        )

    return user #Si existe retorna user