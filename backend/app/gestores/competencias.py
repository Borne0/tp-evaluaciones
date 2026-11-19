from ..pendiente import pendiente
from .base import BaseGestor


class GestorCompetencias(BaseGestor):
    def buscar_competencia(self, nombre): pendiente("CU012")
    def dar_alta_competencia(self, datos): pendiente("CU013")
    def modificar_competencia(self, competencia, nuevos_datos): pendiente("CU014")
    def dar_baja_competencia(self, competencia): pendiente("CU015")
