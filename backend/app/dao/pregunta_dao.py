from sqlalchemy import select

from ..dto import PreguntaCriteriosDTO
from ..entidades.models import Competencia, Factor, Pregunta
from ..pendiente import pendiente
from .base import BaseDAO


class PreguntaDAO(BaseDAO):
    # ---- CU020 (criterios) / CU025 y CU026 (por factor)
    def buscar(self, criterios: PreguntaCriteriosDTO, exacto: bool = False) -> list[Pregunta]:
        """Preguntas vigentes. 'Contiene' por defecto; exacto=True compara los nombres completos."""
        stmt = (
            select(Pregunta)
            .join(Factor, Pregunta.factor_codigo == Factor.codigo)
            .join(Competencia, Factor.competencia_codigo == Competencia.codigo)
            .where(Pregunta.eliminado.is_(False), Factor.eliminado.is_(False), Competencia.eliminado.is_(False))
        )
        for columna, valor in (
            (Competencia.nombre, criterios.nombre_competencia),
            (Factor.nombre, criterios.nombre_factor),
            (Pregunta.nombre_pregunta, criterios.nombre_pregunta),
        ):
            if valor and valor.strip():
                valor = valor.strip()
                stmt = stmt.where(columna == valor if exacto else columna.icontains(valor, autoescape=True))
        return list(self.db.scalars(stmt.order_by(Competencia.nombre, Factor.nombre, Pregunta.nombre_pregunta)))

    def obtener(self, id_pregunta): pendiente()
    def existe_pregunta(self, nombre, enunciado, competencia, factor): pendiente("CU021")
    def insertar(self, pregunta): pendiente("CU021")
    def actualizar(self, pregunta): pendiente("CU022")
    def eliminar(self, pregunta): pendiente("CU023 (baja lógica)")
