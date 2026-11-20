from sqlalchemy.orm import Session

from ..dao import PuestoDAO
from ..dto import CaracteristicaPuestoDTO, PuestoCriteriosDTO, PuestoDTO, PuestoOpcionesDTO
from ..entidades.models import Puesto
from ..pendiente import pendiente
from .base import BaseGestor


class GestorPuestos(BaseGestor):
    def __init__(self, db: Session):
        super().__init__(db)
        self.puesto_dao = PuestoDAO(db)

    # ---- CU008 / CU025 paso 20
    def buscar_puesto(self, criterios: PuestoCriteriosDTO, exacto: bool = False) -> list[PuestoDTO]:
        """Incluye las características (competencias + ponderación mínima), como pide el CU025 paso 23."""
        return [self._a_dto(p) for p in self.puesto_dao.buscar(criterios, exacto)]

    def obtener_opciones_busqueda(self) -> PuestoOpcionesDTO:
        """Valores de los desplegables 'Nombre del puesto' y 'Empresa' (CU025)."""
        nombres, empresas = self.puesto_dao.opciones_busqueda()
        return PuestoOpcionesDTO(nombres=nombres, empresas=empresas)

    def dar_alta_puesto(self, datos): pendiente("CU009")
    def modificar_puesto(self, puesto, nuevos_datos): pendiente("CU010")
    def dar_baja_puesto(self, puesto): pendiente("CU011")
    def buscar_puesto_con_resumen(self, criterios): pendiente("CU028 paso 6 -> List[PuestoResumenDTO]")

    def _a_dto(self, puesto: Puesto) -> PuestoDTO:
        return PuestoDTO(
            codigo=puesto.codigo,
            nombre_puesto=puesto.nombre_puesto,
            descripcion=puesto.descripcion,
            empresa=puesto.empresa,
            caracteristicas=[
                CaracteristicaPuestoDTO(
                    codigo_competencia=c.competencia_codigo,
                    nombre_competencia=c.competencia.nombre,
                    ponderacion_minima_requerida=c.ponderacion_minima_requerida,
                )
                for c in self.puesto_dao.obtener_caracteristicas(puesto)
            ],
        )
