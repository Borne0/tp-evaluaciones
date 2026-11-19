from sqlalchemy import select

from ..entidades.models import Consultor
from .base import BaseDAO


class ConsultorDAO(BaseDAO):
    def obtener_por_username(self, username: str) -> Consultor | None:
        return self.db.scalar(select(Consultor).where(Consultor.username == username))
