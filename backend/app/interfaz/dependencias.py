"""Precondición de los CU del Consultor: 'Actor autenticado en el sistema'."""
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from ..infraestructura.security import decode_token

_bearer = HTTPBearer(auto_error=False)


def consultor_actual(credenciales: HTTPAuthorizationCredentials | None = Depends(_bearer)) -> str:
    """Devuelve el legajo del consultor autenticado (claim `sub` del token)."""
    if credenciales is None:
        raise HTTPException(status_code=401, detail="Debe autenticarse para realizar esta operación")
    try:
        payload = decode_token(credenciales.credentials)
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="La sesión expiró. Vuelva a ingresar")
    if payload.get("perfil") != "CONSULTOR":
        raise HTTPException(status_code=403, detail="No tiene permisos para realizar esta operación")
    return payload["sub"]
