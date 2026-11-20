from ..pendiente import pendiente
from .base import BaseGestor


class GestorPreguntas(BaseGestor):
    def buscar_pregunta(self, criterios): pendiente("CU020 paso 7")
    def dar_alta_pregunta(self, datos): pendiente("CU021 (+ auditoría no aplica)")
    def modificar_pregunta(self, pregunta, nuevos_datos): pendiente("CU022")
    def dar_baja_pregunta(self, pregunta): pendiente("CU023: baja lógica + RegistroAuditoria BAJA_PREGUNTA")
