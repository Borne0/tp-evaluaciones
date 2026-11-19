from ..pendiente import pendiente
from .base import BaseDAO


class PuestoDAO(BaseDAO):
    def buscar(self, criterios): pendiente("CU008 / CU025 / CU028")
    def obtener(self, codigo): pendiente()
    def existe_en_uso(self, puesto): pendiente("CU011")
    def insertar(self, puesto): pendiente("CU009")
    def actualizar(self, puesto): pendiente("CU010")
    def eliminar(self, puesto): pendiente("CU011 (baja lógica)")
    def obtener_caracteristicas(self, puesto): pendiente("CU028 (ponderación mínima por competencia)")
