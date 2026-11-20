from fastapi import HTTPException

from ..gestores.excepciones import CompetenciasNoEvaluables, DatosInvalidos, EntidadEnUso, EntidadNoEncontrada


def a_http(exc: Exception) -> HTTPException:
    """Traduce las excepciones del negocio a respuestas HTTP (misma convención que el router de candidatos)."""
    if isinstance(exc, DatosInvalidos):
        return HTTPException(status_code=400, detail={"errores": exc.errores})
    if isinstance(exc, EntidadNoEncontrada):
        return HTTPException(status_code=404, detail=str(exc))
    if isinstance(exc, (EntidadEnUso, CompetenciasNoEvaluables)):
        return HTTPException(status_code=409, detail=str(exc))
    raise exc


EXCEPCIONES_NEGOCIO = (DatosInvalidos, EntidadNoEncontrada, EntidadEnUso, CompetenciasNoEvaluables)
