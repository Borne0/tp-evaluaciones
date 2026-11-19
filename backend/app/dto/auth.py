from typing import Literal

from pydantic import BaseModel, Field


class ConsultorLoginDTO(BaseModel):
    username: str = Field(min_length=1, max_length=15)   # límite del LDAP
    password: str = Field(min_length=1, max_length=20)   # límite del LDAP


class CandidatoLoginDTO(BaseModel):
    tipo_documento: Literal["DNI", "LE", "LC", "PP"]
    nro_documento: str = Field(min_length=1, max_length=15)
    clave: str = Field(min_length=1, max_length=8)


class TokenDTO(BaseModel):
    token: str
    perfil: Literal["CONSULTOR", "CANDIDATO"]
    nombre: str
    cuestionario_id: int | None = None


__all__ = ["ConsultorLoginDTO", "CandidatoLoginDTO", "TokenDTO"]
