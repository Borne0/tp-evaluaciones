from ..entidades.models import RegistroAuditoria
from .base import BaseDAO


class RegistroAuditoriaDAO(BaseDAO):
    def insertar(self, registro: RegistroAuditoria) -> None:
        self.db.add(registro)
        self.db.flush()
