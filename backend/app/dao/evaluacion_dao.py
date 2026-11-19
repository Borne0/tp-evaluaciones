from ..pendiente import pendiente
from .base import BaseDAO


class EvaluacionDAO(BaseDAO):
    def insertar(self, evaluacion): pendiente("CU025")
    def buscar_por_puesto(self, puesto): pendiente("CU028")
    def obtener(self, id_evaluacion): pendiente()
