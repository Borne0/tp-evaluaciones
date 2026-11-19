from ..pendiente import pendiente
from .base import BaseDAO


class PreguntaDAO(BaseDAO):
    def buscar(self, criterios): pendiente("CU020 (criterios) / CU025 y CU026 (por factor)")
    def obtener(self, id_pregunta): pendiente()
    def existe_pregunta(self, nombre, enunciado, competencia, factor): pendiente("CU021")
    def insertar(self, pregunta): pendiente("CU021")
    def actualizar(self, pregunta): pendiente("CU022")
    def eliminar(self, pregunta): pendiente("CU023 (baja lógica)")
