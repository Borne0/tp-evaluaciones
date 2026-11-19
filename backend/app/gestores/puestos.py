from ..pendiente import pendiente
from .base import BaseGestor


class GestorPuestos(BaseGestor):
    def buscar_puesto(self, criterios): pendiente("CU008 / CU025 paso 20")
    def dar_alta_puesto(self, datos): pendiente("CU009")
    def modificar_puesto(self, puesto, nuevos_datos): pendiente("CU010")
    def dar_baja_puesto(self, puesto): pendiente("CU011")
    def buscar_puesto_con_resumen(self, criterios): pendiente("CU028 paso 6 -> List[PuestoResumenDTO]")
