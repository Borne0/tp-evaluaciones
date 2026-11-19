from ..pendiente import pendiente
from .base import BaseDAO


class FactorDAO(BaseDAO):
    def buscar(self, criterios): pendiente("CU016 / CU021 / CU025")
    def obtener(self, codigo): pendiente()
    def insertar(self, factor): pendiente("CU017")
    def actualizar(self, factor): pendiente("CU018")
    def eliminar(self, factor): pendiente("CU019 (baja lógica)")
