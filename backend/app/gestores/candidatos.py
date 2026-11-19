from ..pendiente import pendiente
from .base import BaseGestor


class GestorCandidatos(BaseGestor):
    def buscar_candidato(self, criterios): pendiente("CU025 paso 4")
    def dar_alta_candidato(self, candidato): pendiente("CU003")
    def dar_baja_candidato(self, candidato): pendiente("CU005")
    def modificar_candidato(self, candidato): pendiente("CU004")
    def importar_candidatos(self, archivo_csv): pendiente("CU006")
    def tiene_cuestionario_activo(self, candidato): pendiente("CU025 paso 12")
