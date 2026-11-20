from ..pendiente import pendiente
from .base import BaseDAO


class CompetenciaDAO(BaseDAO):
    def buscar(self, nombre): pendiente("CU012")
    def obtener(self, codigo): pendiente()
    def esta_en_uso(self, competencia): pendiente("CU015")
    def insertar(self, competencia): pendiente("CU013")
    def actualizar(self, competencia): pendiente("CU014")
    def eliminar(self, competencia): pendiente("CU015 (baja lógica)")
