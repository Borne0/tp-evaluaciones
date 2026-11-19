from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..dto import CandidatoLoginDTO, ConsultorLoginDTO, TokenDTO
from ..gestores.autenticacion import GestorAutenticacion
from ..gestores.excepciones import CredencialesInvalidas
from ..infraestructura.database import get_db
from ..infraestructura.security import create_token

router = APIRouter(prefix="/api/auth", tags=["auth"])

MSG_CONSULTOR = "El usuario o la contraseña no son válidos"
MSG_CANDIDATO = "Los datos ingresados no son válidos o no existe un cuestionario para el Candidato"


@router.post("/consultor", response_model=TokenDTO)
def login_consultor(datos: ConsultorLoginDTO, db: Session = Depends(get_db)):
    try:
        consultor = GestorAutenticacion(db).autenticar_consultor(datos.username, datos.password)
    except CredencialesInvalidas:
        raise HTTPException(status_code=401, detail=MSG_CONSULTOR)
    return TokenDTO(token=create_token(consultor.legajo, "CONSULTOR"), perfil="CONSULTOR", nombre=consultor.username)


@router.post("/candidato", response_model=TokenDTO)
def login_candidato(datos: CandidatoLoginDTO, db: Session = Depends(get_db)):
    try:
        cuestionario = GestorAutenticacion(db).autenticar_candidato(datos.tipo_documento, datos.nro_documento, datos.clave)
    except CredencialesInvalidas:
        raise HTTPException(status_code=401, detail=MSG_CANDIDATO)
    candidato = cuestionario.candidato
    token = create_token(candidato.nro_candidato, "CANDIDATO", cuestionario_id=cuestionario.id_cuestionario)
    return TokenDTO(
        token=token,
        perfil="CANDIDATO",
        nombre=f"{candidato.nombre} {candidato.apellido}",
        cuestionario_id=cuestionario.id_cuestionario,
    )
