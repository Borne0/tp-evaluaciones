from ..pendiente import pendiente
from .base import BaseGestor


class GestorFactores(BaseGestor):
    def buscar_factor(self, criterios): pendiente("CU016 / CU021 paso 'buscarFactor'")
    def dar_alta_factor(self, datos): pendiente("CU017")
    def modificar_factor(self, factor, nuevos_datos): pendiente("CU018")
    def dar_baja_factor(self, factor): pendiente("CU019")
