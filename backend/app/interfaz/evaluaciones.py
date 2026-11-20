"""CU025 – Evaluar Candidatos."""
from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from ..dto import CompetenciaDTO, EvaluacionCreadaDTO, EvaluacionCrearDTO
from ..gestores.evaluaciones import GestorEvaluaciones
from ..infraestructura.database import get_db
from .dependencias import consultor_actual
from .errores import EXCEPCIONES_NEGOCIO, a_http

router = APIRouter(prefix="/api/evaluaciones", tags=["evaluaciones"], dependencies=[Depends(consultor_actual)])

XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


@router.get("/puestos/{codigo}/competencias-no-evaluables", response_model=list[CompetenciaDTO])  # paso 25
def competencias_no_evaluables(codigo: str, db: Session = Depends(get_db)):
    try:
        return GestorEvaluaciones(db).competencias_no_evaluables(codigo)
    except EXCEPCIONES_NEGOCIO as exc:
        raise a_http(exc)


@router.post("", response_model=EvaluacionCreadaDTO, status_code=201)  # pasos 35 a 43
def crear(datos: EvaluacionCrearDTO, db: Session = Depends(get_db)):
    try:
        return GestorEvaluaciones(db).crear_evaluacion(datos.codigo_puesto, datos.nros_candidato)
    except EXCEPCIONES_NEGOCIO as exc:
        raise a_http(exc)


@router.get("/{id_evaluacion}/claves.xlsx")  # pasos 46 a 51
def exportar_claves(id_evaluacion: int, db: Session = Depends(get_db)):
    try:
        contenido = GestorEvaluaciones(db).exportar_claves_excel(id_evaluacion)
    except EXCEPCIONES_NEGOCIO as exc:
        raise a_http(exc)
    return Response(content=contenido, media_type=XLSX)
