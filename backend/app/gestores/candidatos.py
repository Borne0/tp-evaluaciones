"""CU002 – Gestionar Candidatos, CU003 – Alta, CU004 – Modificar, CU005 – Baja."""
import re
from datetime import date, datetime

from sqlalchemy.orm import Session

from ..dao import CandidatoDAO, CuestionarioDAO, RegistroAuditoriaDAO
from ..dto import CandidatoCriteriosDTO, CandidatoDTO
from ..entidades.estados import TIPOS_DOCUMENTO
from ..entidades.models import Candidato, RegistroAuditoria
from ..pendiente import pendiente
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

    # ---- Pendientes
    def importar_candidatos(self, archivo_csv): pendiente("CU006")

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
