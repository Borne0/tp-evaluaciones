from ..entidades.models import Evaluacion
from ..pendiente import pendiente
from .base import BaseDAO


class EvaluacionDAO(BaseDAO):
    def insertar(self, evaluacion: Evaluacion) -> None:
        self.db.add(evaluacion)
        self.db.flush()  # asigna id_evaluacion

    def obtener(self, id_evaluacion: int) -> Evaluacion | None:
        return self.db.get(Evaluacion, id_evaluacion)

    def buscar_por_puesto(self, puesto): pendiente("CU028")
