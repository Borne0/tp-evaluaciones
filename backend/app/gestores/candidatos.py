"""CU002 – Gestionar Candidatos, CU003 – Alta, CU004 – Modificar, CU005 – Baja."""
import csv
import io
import re
import unicodedata
from datetime import date, datetime

from sqlalchemy.orm import Session

from ..dao import CandidatoDAO, CuestionarioDAO, RegistroAuditoriaDAO
from ..dto import CandidatoCriteriosDTO, CandidatoDTO, ImportacionResultadoDTO
from ..entidades.estados import TIPOS_DOCUMENTO
from ..entidades.models import Candidato, RegistroAuditoria
from .base import BaseGestor
from .excepciones import DatosInvalidos, EntidadEnUso, EntidadNoEncontrada

# (atributo, etiqueta, longitud máxima, obligatorio)
_CAMPOS_TEXTO = [
    ("nro_candidato", "Número de candidato", 20, True),
    ("tipo_documento", "Tipo de documento", 3, True),
    ("nro_documento", "Número de documento", 15, True),
    ("apellido", "Apellido", 100, True),
    ("nombre", "Nombre", 100, True),
    ("genero", "Género", 1, False),
    ("nacionalidad", "Nacionalidad", 50, False),
    ("email", "Email", 150, False),
    ("escolaridad", "Escolaridad", 100, False),
]
_SIN_MAYUSCULAS = {"email"}  # los datos literales van en mayúsculas, el email se conserva como se ingresó
# CU006: columnas del CSV (encabezado normalizado -> atributo)
_COLUMNAS_CSV = {
    "nro candidato": "nro_candidato",
    "apellido": "apellido",
    "nombre": "nombre",
    "nro documento": "nro_documento",
    "tipo documento": "tipo_documento",
    "fecha de nacimiento": "fecha_nacimiento",
    "genero": "genero",
    "nacionalidad": "nacionalidad",
    "email": "email",
    "escolaridad": "escolaridad",
    "eliminado": "eliminado",
}
_COLUMNAS_OBLIGATORIAS = {
    "nro_candidato": "Nro candidato",
    "apellido": "Apellido",
    "nombre": "Nombre",
    "nro_documento": "Nro documento",
    "tipo_documento": "Tipo documento",
}
_MAX_ADVERTENCIAS = 20
_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class GestorCandidatos(BaseGestor):
    def __init__(self, db: Session):
        super().__init__(db)
        self.candidato_dao = CandidatoDAO(db)
        self.cuestionario_dao = CuestionarioDAO(db)
        self.auditoria_dao = RegistroAuditoriaDAO(db)

    # ---- CU002
    def buscar_candidato(self, criterios: CandidatoCriteriosDTO) -> list[CandidatoDTO]:
        return [self._a_dto(c) for c in self.candidato_dao.buscar(criterios)]

    def obtener_candidato(self, nro_candidato: str) -> CandidatoDTO:
        return self._a_dto(self._obtener_vigente(nro_candidato))

    # ---- CU003
    def dar_alta_candidato(self, datos: CandidatoDTO) -> CandidatoDTO:
        datos, errores = self._normalizar_y_validar(datos)
        if not errores:
            existente = self.candidato_dao.obtener(datos.nro_candidato)
            if existente is not None:
                errores.append(f"Ya existe un candidato con el número {datos.nro_candidato}" + (" (dado de baja)." if existente.eliminado else "."))
            por_doc = self.candidato_dao.obtener_por_documento(datos.tipo_documento, datos.nro_documento)
            if por_doc is not None:
                errores.append(f"Ya existe un candidato con el documento {datos.tipo_documento} {datos.nro_documento}.")
        if errores:
            raise DatosInvalidos(errores)

        candidato = Candidato(**datos.model_dump())
        self.candidato_dao.insertar(candidato)
        self.db.commit()
        return self._a_dto(candidato)

    # ---- CU004
    def modificar_candidato(self, datos: CandidatoDTO) -> CandidatoDTO:
        candidato = self._obtener_vigente(datos.nro_candidato)  # el número no es editable
        datos, errores = self._normalizar_y_validar(datos)
        if not errores:
            por_doc = self.candidato_dao.obtener_por_documento(datos.tipo_documento, datos.nro_documento)
            if por_doc is not None and por_doc.nro_candidato != candidato.nro_candidato:
                errores.append(f"Ya existe otro candidato con el documento {datos.tipo_documento} {datos.nro_documento}.")
        if errores:
            raise DatosInvalidos(errores)

        for campo, valor in datos.model_dump(exclude={"nro_candidato"}).items():
            setattr(candidato, campo, valor)
        self.candidato_dao.actualizar(candidato)
        self.db.commit()
        return self._a_dto(candidato)

    # ---- CU005
    def validar_baja_candidato(self, nro_candidato: str) -> CandidatoDTO:
        """Paso 2 del CU: constata que el candidato no esté en uso (cuestionario activo o en proceso)."""
        candidato = self._obtener_vigente(nro_candidato)
        if self.tiene_cuestionario_activo(candidato.nro_candidato):
            raise EntidadEnUso(
                f"El candidato {candidato.apellido} {candidato.nombre} tiene un cuestionario activo o en proceso y no puede eliminarse."
            )
        return self._a_dto(candidato)

    def dar_baja_candidato(self, nro_candidato: str, consultor_legajo: str) -> None:
        candidato = self._obtener_vigente(nro_candidato)
        self.validar_baja_candidato(nro_candidato)
        self.candidato_dao.eliminar(candidato)  # baja lógica
        ahora = datetime.now()
        self.auditoria_dao.insertar(RegistroAuditoria(
            fecha=ahora.date(), hora=ahora.strftime("%H:%M:%S"), accion="BAJA_CANDIDATO",
            entidad_afectada="Candidato", id_entidad_afectada=candidato.nro_candidato, consultor_legajo=consultor_legajo,
        ))
        self.db.commit()

    # ---- CU006
    def importar_candidatos(self, contenido: bytes) -> ImportacionResultadoDTO:
        """Importa el CSV del sistema de Gestión de Candidatos y CV. La clave única es el Nro de candidato.

        - No existe y Eliminado=False -> se crea.  Existe y cambió algún dato -> se actualiza.
        - Eliminado=True sobre un candidato existente -> baja lógica (si tiene un cuestionario activo o en proceso se omite).
        Las filas con errores se omiten y se informan; el resto se importa en una única transacción.
        """
        filas = self._leer_csv(contenido)
        creados = actualizados = eliminados = omitidos = 0
        advertencias: list[str] = []

        for nro_fila, fila in filas:
            try:
                resultado = self._importar_fila(fila)
            except DatosInvalidos as exc:
                omitidos += 1
                if len(advertencias) < _MAX_ADVERTENCIAS:
                    advertencias.append(f"Fila {nro_fila}: {' '.join(exc.errores)}")
                continue
            creados += resultado == "creado"
            actualizados += resultado == "actualizado"
            eliminados += resultado == "eliminado"

        self.db.commit()
        if omitidos > len(advertencias):
            advertencias.append(f"…y {omitidos - len(advertencias)} fila(s) más con errores.")
        return ImportacionResultadoDTO(
            cantidad_creados=creados, cantidad_actualizados=actualizados, cantidad_eliminados=eliminados,
            cantidad_omitidos=omitidos, advertencias=advertencias,
        )

    @staticmethod
    def _clave_columna(encabezado: str) -> str:
        sin_acentos = "".join(ch for ch in unicodedata.normalize("NFKD", encabezado) if not unicodedata.combining(ch))
        sin_formato = re.sub(r"\(.*?\)", "", sin_acentos)  # "Fecha de nacimiento (aaaa-mm-dd)"
        return " ".join(sin_formato.lower().split())

    def _leer_csv(self, contenido: bytes) -> list[tuple[int, dict[str, str]]]:
        if not contenido.strip():
            raise DatosInvalidos(["El archivo está vacío."])
        try:
            texto = contenido.decode("utf-8-sig")  # utf-8, con o sin BOM (Excel lo agrega)
        except UnicodeDecodeError:
            texto = contenido.decode("cp1252", errors="replace")

        try:
            lector = csv.reader(io.StringIO(texto, newline=""), delimiter=";")
            encabezado = next(lector)
            columnas = [_COLUMNAS_CSV.get(self._clave_columna(c)) for c in encabezado]
            faltantes = [etiqueta for attr, etiqueta in _COLUMNAS_OBLIGATORIAS.items() if attr not in columnas]
            if faltantes:
                ayuda = " Verifique que las columnas estén separadas por punto y coma (;)." if len(encabezado) == 1 else ""
                raise DatosInvalidos(["Faltan columnas obligatorias en el encabezado: " + ", ".join(faltantes) + "." + ayuda])
            filas = [
                (i, {col: valor for col, valor in zip(columnas, valores) if col})
                for i, valores in enumerate(lector, start=2)
                if any(v.strip() for v in valores)
            ]
        except csv.Error:
            raise DatosInvalidos(["El archivo no tiene un formato CSV válido."])

        if not filas:
            raise DatosInvalidos(["El archivo no contiene candidatos para importar."])
        return filas

    def _importar_fila(self, fila: dict[str, str]) -> str | None:
        """Devuelve 'creado', 'actualizado', 'eliminado' o None (sin cambios). Lanza DatosInvalidos si la fila no es válida."""
        errores: list[str] = []

        fecha = None
        texto_fecha = (fila.get("fecha_nacimiento") or "").strip()
        if texto_fecha:
            try:
                fecha = date.fromisoformat(texto_fecha)
            except ValueError:
                errores.append("La fecha de nacimiento debe tener el formato aaaa-mm-dd.")

        texto_baja = (fila.get("eliminado") or "").strip().lower()
        if texto_baja in ("true", "1", "si", "sí"):
            baja = True
        elif texto_baja in ("", "false", "0", "no"):
            baja = False
        else:
            baja = False
            errores.append("Eliminado debe ser True o False.")

        dto = CandidatoDTO(
            nro_candidato=fila.get("nro_candidato") or "", tipo_documento=fila.get("tipo_documento") or "",
            nro_documento=fila.get("nro_documento") or "", apellido=fila.get("apellido") or "",
            nombre=fila.get("nombre") or "", fecha_nacimiento=fecha, genero=fila.get("genero") or None,
            nacionalidad=fila.get("nacionalidad") or None, email=fila.get("email") or None,
            escolaridad=fila.get("escolaridad") or None,
        )
        dto, errores_validacion = self._normalizar_y_validar(dto)
        errores += errores_validacion
        if errores:
            raise DatosInvalidos(errores)

        por_doc = self.candidato_dao.obtener_por_documento(dto.tipo_documento, dto.nro_documento)
        if por_doc is not None and por_doc.nro_candidato != dto.nro_candidato:
            raise DatosInvalidos([f"El documento {dto.tipo_documento} {dto.nro_documento} ya pertenece al candidato {por_doc.nro_candidato}."])

        existente = self.candidato_dao.obtener(dto.nro_candidato)
        if existente is None:
            if baja:
                return None  # nada que eliminar
            self.candidato_dao.insertar(Candidato(**dto.model_dump()))
            return "creado"

        if baja:
            if existente.eliminado:
                return None
            if self.tiene_cuestionario_activo(existente.nro_candidato):
                raise DatosInvalidos([f"El candidato {existente.nro_candidato} tiene un cuestionario activo o en proceso y no se eliminó."])
            self.candidato_dao.eliminar(existente)
            return "eliminado"

        datos = dto.model_dump(exclude={"nro_candidato"})
        if not existente.eliminado and all(getattr(existente, k) == v for k, v in datos.items()):
            return None
        for campo, valor in datos.items():
            setattr(existente, campo, valor)
        existente.eliminado = False  # reactivación si venía dado de baja
        self.candidato_dao.actualizar(existente)
        return "actualizado"

    # ---- Pendientes
    def tiene_cuestionario_activo(self, nro_candidato: str) -> bool:
        return self.cuestionario_dao.obtener_activo_o_en_proceso(nro_candidato) is not None

    # ---- Internos
    def _obtener_vigente(self, nro_candidato: str) -> Candidato:
        candidato = self.candidato_dao.obtener(nro_candidato)
        if candidato is None or candidato.eliminado:
            raise EntidadNoEncontrada("El candidato no existe.")
        return candidato

    @staticmethod
    def _a_dto(candidato: Candidato) -> CandidatoDTO:
        return CandidatoDTO.model_validate(candidato, from_attributes=True)

    @staticmethod
    def _normalizar_y_validar(datos: CandidatoDTO) -> tuple[CandidatoDTO, list[str]]:
        """Devuelve los datos normalizados y TODAS las omisiones / errores encontrados."""
        valores = datos.model_dump()
        errores: list[str] = []
        faltantes: list[str] = []
        for attr, etiqueta, maximo, obligatorio in _CAMPOS_TEXTO:
            v = (valores[attr] or "").strip()
            if attr not in _SIN_MAYUSCULAS:
                v = v.upper()
            valores[attr] = v or None
            if not v:
                if obligatorio:
                    faltantes.append(etiqueta)
            elif len(v) > maximo:
                errores.append(f"{etiqueta} excede la longitud máxima de {maximo} caracteres.")
        if faltantes:
            errores.insert(0, "Falta ingresar: " + ", ".join(faltantes) + ".")

        if valores["tipo_documento"] and valores["tipo_documento"] not in TIPOS_DOCUMENTO:
            errores.append("Tipo de documento inválido (DNI, LE, LC o PP).")
        if valores["genero"] and valores["genero"] not in ("H", "M"):
            errores.append("Género inválido (H o M).")
        if valores["email"] and not _EMAIL.match(valores["email"]):
            errores.append("El email no tiene un formato válido.")
        if valores["fecha_nacimiento"] and valores["fecha_nacimiento"] > date.today():
            errores.append("La fecha de nacimiento no puede ser futura.")
        return CandidatoDTO(**valores) if not faltantes else datos, errores
