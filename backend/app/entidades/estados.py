class EstadoCuestionario:
    ACTIVO = "Activo"
    EN_PROCESO = "En Proceso"
    COMPLETO = "Completo"
    INCOMPLETO = "Incompleto"
    SIN_CONTESTAR = "Sin Contestar"
    ABIERTOS = (ACTIVO, EN_PROCESO)  # "activo o en proceso"


class EstadoEvaluacion:
    ACTIVA = "Activa"


class TipoCompetencia:
    TECNICA = "Técnica"
    ACTITUDINAL = "Actitudinal"


TIPOS_DOCUMENTO = ("DNI", "LE", "LC", "PP")
