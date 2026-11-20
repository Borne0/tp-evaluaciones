"""Generación del Excel de claves de ingreso (CU025 pasos 44-51)."""
from io import BytesIO

from openpyxl import Workbook
from openpyxl.styles import Font

from ..dto import CandidatoClaveDTO

_ENCABEZADO = ["Nro candidato", "Apellido", "Nombre", "Tipo documento", "Nro documento", "Clave de ingreso"]
_ANCHOS = [16, 24, 24, 16, 18, 18]


def claves_a_xlsx(claves: list[CandidatoClaveDTO]) -> bytes:
    libro = Workbook()
    hoja = libro.active
    hoja.title = "Claves"
    hoja.append(_ENCABEZADO)
    for celda in hoja[1]:
        celda.font = Font(bold=True)
    for c in claves:
        hoja.append([c.nro_candidato, c.apellido, c.nombre, c.tipo_documento, c.nro_documento, c.clave_ingreso])

    for fila in hoja.iter_rows(min_row=2):
        for celda in fila:
            # los datos vienen de una importación: nunca deben interpretarse como fórmulas
            if isinstance(celda.value, str) and celda.value[:1] in ("=", "+", "-", "@"):
                celda.data_type = "s"
    for i, ancho in enumerate(_ANCHOS):
        hoja.column_dimensions[chr(ord("A") + i)].width = ancho

    salida = BytesIO()
    libro.save(salida)
    return salida.getvalue()
