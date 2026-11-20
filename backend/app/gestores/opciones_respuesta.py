from ..pendiente import pendiente
from .base import BaseGestor


class GestorOpcionesRespuesta(BaseGestor):
    def buscar_opcion(self, nombre): pendiente("CU024")
    def dar_alta_opcion(self, datos): pendiente("CU029")
    def modificar_opcion(self, opcion, nuevos_datos): pendiente("CU030")
    def dar_baja_opcion(self, opcion): pendiente("CU031")
