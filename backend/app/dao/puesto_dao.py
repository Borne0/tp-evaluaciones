from sqlalchemy import select

from ..dto import PuestoCriteriosDTO
from ..entidades.models import CaracteristicaPuesto, Competencia, Puesto
from ..pendiente import pendiente
from .base import BaseDAO


class PuestoDAO(BaseDAO):
    # ---- CU008 / CU025 / CU028
    def buscar(self, criterios: PuestoCriteriosDTO, exacto: bool = False) -> list[Puesto]:
        """Puestos no eliminados. Por defecto el criterio es 'contiene'; con exacto=True se compara el valor completo."""
        stmt = select(Puesto).where(Puesto.eliminado.is_(False))
        for columna, valor in (
            (Puesto.codigo, criterios.codigo),
            (Puesto.nombre_puesto, criterios.nombre_puesto),
            (Puesto.empresa, criterios.empresa),
        ):
            if valor and valor.strip():
                valor = valor.strip()
                stmt = stmt.where(columna == valor if exacto else columna.icontains(valor, autoescape=True))
        return list(self.db.scalars(stmt.order_by(Puesto.nombre_puesto, Puesto.empresa)))

    def obtener(self, codigo: str) -> Puesto | None:
        return self.db.get(Puesto, codigo)

    def obtener_caracteristicas(self, puesto: Puesto) -> list[CaracteristicaPuesto]:
        """Competencias (vigentes) del puesto con su ponderación mínima requerida."""
        stmt = (
            select(CaracteristicaPuesto)
            .join(Competencia, CaracteristicaPuesto.competencia_codigo == Competencia.codigo)
            .where(CaracteristicaPuesto.puesto_codigo == puesto.codigo, Competencia.eliminado.is_(False))
            .order_by(Competencia.nombre)
        )
        return list(self.db.scalars(stmt))

    def opciones_busqueda(self) -> tuple[list[str], list[str]]:
        """Nombres de puesto y empresas distintos (para los desplegables del CU025)."""
        base = select(Puesto).where(Puesto.eliminado.is_(False)).subquery()
        nombres = self.db.scalars(select(base.c.nombre_puesto).distinct().order_by(base.c.nombre_puesto))
        empresas = self.db.scalars(select(base.c.empresa).distinct().order_by(base.c.empresa))
        return list(nombres), list(empresas)

    def existe_en_uso(self, puesto): pendiente("CU011")
    def insertar(self, puesto): pendiente("CU009")
    def actualizar(self, puesto): pendiente("CU010")
    def eliminar(self, puesto): pendiente("CU011 (baja lógica)")
