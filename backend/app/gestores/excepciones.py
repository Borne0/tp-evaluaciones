class CredencialesInvalidas(Exception):
    """Usuario/contraseña inválidos (consultor) o candidato/cuestionario/clave inválidos."""


class DatosInvalidos(Exception):
    """Datos faltantes o inválidos. Lleva TODAS las omisiones/errores detectados (los CU piden detallarlos todos)."""

    def __init__(self, errores: list[str]):
        super().__init__("; ".join(errores))
        self.errores = errores


class EntidadNoEncontrada(Exception):
    """La entidad pedida no existe (o está dada de baja)."""


class EntidadEnUso(Exception):
    """La entidad no puede eliminarse porque está siendo usada."""
