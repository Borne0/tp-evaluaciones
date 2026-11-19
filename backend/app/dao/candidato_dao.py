from sqlalchemy import select

from ..entidades.models import Candidato
from ..pendiente import pendiente
from .base import BaseDAO


class CandidatoDAO(BaseDAO):
    def obtener_por_documento(self, tipo_documento: str, nro_documento: str) -> Candidato | None:
        return self.db.scalar(
            select(Candidato).where(Candidato.tipo_documento == tipo_documento, Candidato.nro_documento == nro_documento)
        )

    def buscar(self, criterios): pendiente("CU025 / CU002")
    def obtener(self, nro_candidato): pendiente()
    def insertar(self, candidato): pendiente("CU003 / CU006")
    def actualizar(self, candidato): pendiente("CU004 / CU006")
    def eliminar(self, candidato): pendiente("CU005")
    def contar_por_puesto(self, puesto): pendiente("CU028")
