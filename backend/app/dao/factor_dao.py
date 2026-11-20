from sqlalchemy import select

from ..dto import FactorCriteriosDTO
from ..entidades.models import Competencia, Factor
from ..pendiente import pendiente
from .base import BaseDAO


class FactorDAO(BaseDAO):
    # ---- CU016 / CU021 / CU025
    def buscar(self, criterios: FactorCriteriosDTO, exacto: bool = False) -> list[Factor]:
        """Factores vigentes (de competencias vigentes). 'Contiene' por defecto; exacto=True compara el nombre completo."""
        stmt = (
            select(Factor)
            .join(Competencia, Factor.competencia_codigo == Competencia.codigo)
            .where(Factor.eliminado.is_(False), Competencia.eliminado.is_(False))
        )
        for columna, valor in ((Competencia.nombre, criterios.nombre_competencia), (Factor.nombre, criterios.nombre_factor)):
            if valor and valor.strip():
                valor = valor.strip()
                stmt = stmt.where(columna == valor if exacto else columna.icontains(valor, autoescape=True))
        return list(self.db.scalars(stmt.order_by(Factor.nombre)))

    def obtener(self, codigo): pendiente()
    def insertar(self, factor): pendiente("CU017")
    def actualizar(self, factor): pendiente("CU018")
    def eliminar(self, factor): pendiente("CU019 (baja lógica)")
