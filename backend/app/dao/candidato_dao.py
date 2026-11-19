from sqlalchemy import select

from ..dto import CandidatoCriteriosDTO
from ..entidades.models import Candidato
from ..pendiente import pendiente
from .base import BaseDAO


class CandidatoDAO(BaseDAO):
    def obtener_por_documento(self, tipo_documento: str, nro_documento: str) -> Candidato | None:
        return self.db.scalar(
            select(Candidato).where(Candidato.tipo_documento == tipo_documento, Candidato.nro_documento == nro_documento)
        )

    # ---- CU002 / CU025
    def buscar(self, criterios: CandidatoCriteriosDTO) -> list[Candidato]:
        """Candidatos no eliminados; criterio 'contiene', sin distinguir mayúsculas. Sin criterios devuelve todos."""
        stmt = select(Candidato).where(Candidato.eliminado.is_(False))
        if criterios.apellido:
            stmt = stmt.where(Candidato.apellido.icontains(criterios.apellido.strip(), autoescape=True))
        if criterios.nombre:
            stmt = stmt.where(Candidato.nombre.icontains(criterios.nombre.strip(), autoescape=True))
        if criterios.nro_candidato:
            stmt = stmt.where(Candidato.nro_candidato.icontains(criterios.nro_candidato.strip(), autoescape=True))
        return list(self.db.scalars(stmt.order_by(Candidato.apellido, Candidato.nombre, Candidato.nro_candidato)))

    def obtener(self, nro_candidato: str) -> Candidato | None:
        """Incluye eliminados (para validar claves duplicadas); el Gestor decide qué hacer con ellos."""
        return self.db.get(Candidato, nro_candidato)

    # ---- CU003 / CU006
    def insertar(self, candidato: Candidato) -> None:
        self.db.add(candidato)
        self.db.flush()

    # ---- CU004 / CU006
    def actualizar(self, candidato: Candidato) -> None:
        self.db.flush()  # la entidad ya está en la sesión; solo se vuelcan los cambios

    # ---- CU005
    def eliminar(self, candidato: Candidato) -> None:
        """Baja lógica."""
        candidato.eliminado = True
        self.db.flush()

    def contar_por_puesto(self, puesto): pendiente("CU028")
