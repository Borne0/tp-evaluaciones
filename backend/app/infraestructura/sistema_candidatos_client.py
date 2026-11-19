"""Sistema de Gestión de Candidatos y CV – HTTPS / REST (importación CU006 / exportación CU007)."""
from ..dto import CandidatoDTO, ResultadoExportadoDTO
from ..pendiente import pendiente


class SistemaCandidatosClient:
    def obtener_candidatos(self) -> list[CandidatoDTO]:
        pendiente("CU006")

    def enviar_resultados(self, resultados: list[ResultadoExportadoDTO]) -> None:
        pendiente("CU007")
