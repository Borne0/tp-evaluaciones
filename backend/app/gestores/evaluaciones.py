from ..pendiente import pendiente
from .base import BaseGestor


class GestorEvaluaciones(BaseGestor):
    # Diagrama de clases
    def crear_evaluacion(self, puesto, lista_candidatos): pendiente("CU025 paso 35")
    def registrar_respuesta_bloque(self, bloque): pendiente("CU026 paso 37")
    def calcular_resultados_cuestionario(self, cuestionario): pendiente("CU026 paso 44")
    def emitir_reporte_comparativo(self, candidato, puesto): pendiente("CU027")
    def generar_orden_merito(self, puesto, evaluacion_seleccionada): pendiente("CU028 paso 21")
    def exportar_claves(self, evaluacion): pendiente("CU025 paso 46")
    def exportar_resultados(self, criterios): pendiente("CU007")

    # Agregados por los diagramas de secuencia
    def validar_competencias_evaluables(self, puesto): pendiente("CU025 paso 25 (factores con >= 2 preguntas)")
    def generar_clave_aleatoria(self) -> str: pendiente("CU025 paso 39 (8 caracteres: letras y dígitos)")
    def obtener_cuestionario_para_completar(self, candidato): pendiente("CU026 paso 2")
    def armar_cuestionario(self, cuestionario): pendiente("CU026 paso 16 (2 preguntas al azar por factor)")
    def obtener_bloque_pendiente(self, cuestionario): pendiente("CU026 paso 32")
