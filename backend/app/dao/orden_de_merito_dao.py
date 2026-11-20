from ..pendiente import pendiente
from .base import BaseDAO


class OrdenDeMeritoDAO(BaseDAO):
    def insertar(self, orden_de_merito): pendiente("CU028")
    def obtener_por_evaluaciones(self, evaluaciones): pendiente("CU028")
