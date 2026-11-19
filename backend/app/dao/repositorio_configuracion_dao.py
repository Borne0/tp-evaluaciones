from ..pendiente import pendiente
from .base import BaseDAO


class RepositorioConfiguracionDAO(BaseDAO):
    """Aparece en el diagrama de secuencia del CU026 (no en el diagrama de clases)."""

    def obtener_parametros(self): pendiente("CU026: ConfiguracionDTO")
