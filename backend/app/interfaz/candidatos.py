"""CU002 – Gestionar Candidatos (+ CU003 alta, CU004 modificar, CU005 baja)."""
from fastapi import APIRouter, Depends, File, HTTPException, Query, Response, UploadFile
from sqlalchemy.orm import Session

from ..dto import CandidatoCriteriosDTO, CandidatoDTO, ImportacionResultadoDTO
from ..gestores.candidatos import GestorCandidatos
from ..gestores.excepciones import DatosInvalidos, EntidadEnUso, EntidadNoEncontrada
from ..infraestructura.database import get_db
from .dependencias import consultor_actual

router = APIRouter(prefix="/api/candidatos", tags=["candidatos"], dependencies=[Depends(consultor_actual)])


MAX_CSV_BYTES = 10 * 1024 * 1024  # 10 MB


def _http(exc: Exception) -> HTTPException:
    if isinstance(exc, DatosInvalidos):
        return HTTPException(status_code=400, detail={"errores": exc.errores})
    if isinstance(exc, EntidadNoEncontrada):
        return HTTPException(status_code=404, detail=str(exc))
    if isinstance(exc, EntidadEnUso):
        return HTTPException(status_code=409, detail=str(exc))
    raise exc


@router.get("", response_model=list[CandidatoDTO])
def buscar(
    apellido: str | None = Query(None, max_length=100),
    nombre: str | None = Query(None, max_length=100),
    nro_candidato: str | None = Query(None, max_length=20),
    db: Session = Depends(get_db),
):
    criterios = CandidatoCriteriosDTO(apellido=apellido, nombre=nombre, nro_candidato=nro_candidato)
    return GestorCandidatos(db).buscar_candidato(criterios)


@router.post("", response_model=CandidatoDTO, status_code=201)  # CU003
def alta(datos: CandidatoDTO, db: Session = Depends(get_db)):
    try:
        return GestorCandidatos(db).dar_alta_candidato(datos)
    except (DatosInvalidos, EntidadNoEncontrada, EntidadEnUso) as exc:
        raise _http(exc)


@router.post("/importar", response_model=ImportacionResultadoDTO)  # CU006
def importar(archivo: UploadFile = File(...), db: Session = Depends(get_db)):
    contenido = archivo.file.read(MAX_CSV_BYTES + 1)
    if len(contenido) > MAX_CSV_BYTES:
        raise HTTPException(status_code=413, detail="El archivo supera el tamaño máximo permitido (10 MB).")
    try:
        return GestorCandidatos(db).importar_candidatos(contenido)
    except DatosInvalidos as exc:
        raise _http(exc)


@router.get("/{nro_candidato}", response_model=CandidatoDTO)
def obtener(nro_candidato: str, db: Session = Depends(get_db)):
    try:
        return GestorCandidatos(db).obtener_candidato(nro_candidato)
    except EntidadNoEncontrada as exc:
        raise _http(exc)


@router.put("/{nro_candidato}", response_model=CandidatoDTO)  # CU004
def modificar(nro_candidato: str, datos: CandidatoDTO, db: Session = Depends(get_db)):
    datos.nro_candidato = nro_candidato  # el número no es editable
    try:
        return GestorCandidatos(db).modificar_candidato(datos)
    except (DatosInvalidos, EntidadNoEncontrada, EntidadEnUso) as exc:
        raise _http(exc)


@router.get("/{nro_candidato}/puede-eliminarse", status_code=204)  # CU005 paso 2
def puede_eliminarse(nro_candidato: str, db: Session = Depends(get_db)):
    try:
        GestorCandidatos(db).validar_baja_candidato(nro_candidato)
    except (EntidadNoEncontrada, EntidadEnUso) as exc:
        raise _http(exc)
    return Response(status_code=204)


@router.delete("/{nro_candidato}", status_code=204)  # CU005 paso 3
def baja(nro_candidato: str, legajo: str = Depends(consultor_actual), db: Session = Depends(get_db)):
    try:
        GestorCandidatos(db).dar_baja_candidato(nro_candidato, legajo)
    except (EntidadNoEncontrada, EntidadEnUso) as exc:
        raise _http(exc)
    return Response(status_code=204)
