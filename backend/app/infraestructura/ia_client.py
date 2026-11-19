"""Servicio de IA (GenAI) – HTTPS / REST (JSON). Usado por CU021/033 (preguntas) y CU009 (puestos)."""
from ..dto import PreguntaDTO, PuestoDTO
from ..pendiente import pendiente


class ServicioIA:
    def generar_pregunta(self, codigo_competencia: str, codigo_factor: str) -> PreguntaDTO:
        pendiente("CU033: invocar la API de generación de preguntas")

    def generar_puesto(self, descripcion: str) -> PuestoDTO:
        pendiente("CU009: invocar la API de generación de puestos")
