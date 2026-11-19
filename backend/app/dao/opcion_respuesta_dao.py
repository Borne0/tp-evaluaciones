from ..pendiente import pendiente
from .base import BaseDAO


class OpcionRespuestaDAO(BaseDAO):
    def buscar(self, nombre): pendiente("CU024")
    def obtener(self, id_opcion): pendiente()
    def esta_en_uso(self, opcion): pendiente("CU031")
    def insertar(self, opcion): pendiente("CU029")
    def actualizar(self, opcion): pendiente("CU030")
    def eliminar(self, opcion): pendiente("CU031 (baja lógica)")
