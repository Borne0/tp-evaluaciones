"""Consulta de puestos (CU025). El resto del CU008 se agrega al implementarlo."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..dto import PuestoCriteriosDTO, PuestoDTO, PuestoOpcionesDTO
from ..gestores.puestos import GestorPuestos
from ..infraestructura.database import get_db
from .dependencias import consultor_actual

router = APIRouter(prefix="/api/puestos", tags=["puestos"], dependencies=[Depends(consultor_actual)])


@router.get("/opciones", response_model=PuestoOpcionesDTO)
def opciones(db: Session = Depends(get_db)):
    return GestorPuestos(db).obtener_opciones_busqueda()


@router.get("", response_model=list[PuestoDTO])
def buscar(
    codigo: str | None = Query(None, max_length=50),
    nombre_puesto: str | None = Query(None, max_length=300),
    empresa: str | None = Query(None, max_length=100),
    exacto: bool = False,
    db: Session = Depends(get_db),
):
    criterios = PuestoCriteriosDTO(codigo=codigo, nombre_puesto=nombre_puesto, empresa=empresa)
    return GestorPuestos(db).buscar_puesto(criterios, exacto)
