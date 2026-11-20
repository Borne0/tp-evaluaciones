import secrets
from datetime import date

from sqlalchemy.orm import Session

from ..dao import CandidatoDAO, CuestionarioDAO, EvaluacionDAO, FactorDAO, PreguntaDAO, PuestoDAO
from ..dto import (CandidatoClaveDTO, CompetenciaDTO, EvaluacionCreadaDTO, FactorCriteriosDTO,
                   PreguntaCriteriosDTO)
from ..entidades.estados import EstadoCuestionario, EstadoEvaluacion
from ..entidades.models import Candidato, Cuestionario, Evaluacion
from ..infraestructura.excel import claves_a_xlsx
from ..pendiente import pendiente
from .base import BaseGestor
from .excepciones import CompetenciasNoEvaluables, DatosInvalidos, EntidadEnUso, EntidadNoEncontrada

_LETRAS = "ABCDEFGHJKLMNPQRSTUVWXYZ"  # sin I ni O: la clave se comunica por teléfono
_DIGITOS = "23456789"  # sin 0 ni 1
LARGO_CLAVE = 8
MIN_PREGUNTAS_POR_FACTOR = 2


class GestorEvaluaciones(BaseGestor):
    def __init__(self, db: Session):
        super().__init__(db)
        self.puesto_dao = PuestoDAO(db)
        self.candidato_dao = CandidatoDAO(db)
        self.cuestionario_dao = CuestionarioDAO(db)
        self.evaluacion_dao = EvaluacionDAO(db)
        self.factor_dao = FactorDAO(db)
        self.pregunta_dao = PreguntaDAO(db)

    # ---------------- CU025 ----------------
    def competencias_no_evaluables(self, codigo_puesto: str) -> list[CompetenciaDTO]:
        puesto = self._obtener_puesto(codigo_puesto)
        if not self.puesto_dao.obtener_caracteristicas(puesto):
            raise DatosInvalidos(["El puesto seleccionado no tiene competencias asociadas."])
        return self.validar_competencias_evaluables(puesto)

    def validar_competencias_evaluables(self, puesto) -> list[CompetenciaDTO]:
        """Paso 25: una competencia es evaluable si tiene al menos un factor con 2 o más preguntas."""
        no_evaluables: list[CompetenciaDTO] = []
        for caracteristica in self.puesto_dao.obtener_caracteristicas(puesto):
            competencia = caracteristica.competencia
            factores = self.factor_dao.buscar(FactorCriteriosDTO(nombre_competencia=competencia.nombre), exacto=True)
            evaluable = any(
                len(self.pregunta_dao.buscar(
                    PreguntaCriteriosDTO(nombre_competencia=competencia.nombre, nombre_factor=f.nombre), exacto=True
                )) >= MIN_PREGUNTAS_POR_FACTOR
                for f in factores
            )
            if not evaluable:
                no_evaluables.append(CompetenciaDTO.model_validate(competencia, from_attributes=True))
        return no_evaluables

    def crear_evaluacion(self, codigo_puesto: str, nros_candidato: list[str]) -> EvaluacionCreadaDTO:
        """Pasos 35-43. Revalida todo en el servidor (no se confía en lo que validó la pantalla)."""
        errores = []
        if not (codigo_puesto or "").strip():
            errores.append("Debe seleccionar un puesto / función.")
        nros = list(dict.fromkeys(n.strip() for n in nros_candidato if n and n.strip()))
        if not nros:
            errores.append("Debe seleccionar al menos un candidato para evaluar.")
        if errores:
            raise DatosInvalidos(errores)

        puesto = self._obtener_puesto(codigo_puesto)

        candidatos: list[Candidato] = []
        for nro in nros:
            c = self.candidato_dao.obtener(nro)
            if c is None or c.eliminado:
                raise DatosInvalidos([f"El candidato {nro} no existe."])
            candidatos.append(c)

        # 6.A – candidatos que ya tienen un cuestionario activo o en proceso
        en_uso = [c for c in candidatos if self.tiene_cuestionario_activo(c.nro_candidato)]
        if en_uso:
            nombres = ", ".join(f"{c.apellido} {c.nombre}" for c in en_uso)
            raise EntidadEnUso(
                "Los siguientes candidatos poseen cuestionarios activos o en proceso y no pueden ser evaluados nuevamente: "
                f"{nombres}."
            )

        # 9.A – competencias del puesto que no pueden evaluarse
        if not self.puesto_dao.obtener_caracteristicas(puesto):
            raise DatosInvalidos(["El puesto seleccionado no tiene competencias asociadas."])
        no_evaluables = self.validar_competencias_evaluables(puesto)
        if no_evaluables:
            raise CompetenciasNoEvaluables([c.nombre for c in no_evaluables])

        evaluacion = Evaluacion(fecha_creacion=date.today(), estado=EstadoEvaluacion.ACTIVA, puesto_codigo=puesto.codigo)
        self.evaluacion_dao.insertar(evaluacion)

        claves: list[CandidatoClaveDTO] = []
        for c in candidatos:
            cuestionario = Cuestionario(
                clave_ingreso=self.generar_clave_aleatoria(),
                estado=EstadoCuestionario.ACTIVO,
                evaluacion_id=evaluacion.id_evaluacion,
                candidato_nro_candidato=c.nro_candidato,
            )
            self.cuestionario_dao.insertar(cuestionario)
            claves.append(self._clave_dto(c, cuestionario))
        self.db.commit()

        claves.sort(key=lambda k: (k.apellido, k.nombre, k.nro_candidato))
        return EvaluacionCreadaDTO(
            id_evaluacion=evaluacion.id_evaluacion,
            codigo_puesto=puesto.codigo,
            nombre_puesto=puesto.nombre_puesto,
            empresa=puesto.empresa,
            fecha_creacion=evaluacion.fecha_creacion,
            claves=claves,
        )

    def exportar_claves(self, id_evaluacion: int) -> list[CandidatoClaveDTO]:
        """Pasos 46-47: candidatos de la evaluación con su clave de ingreso."""
        if self.evaluacion_dao.obtener(id_evaluacion) is None:
            raise EntidadNoEncontrada("La evaluación no existe.")
        return [self._clave_dto(c.candidato, c) for c in self.cuestionario_dao.buscar_por_evaluacion(id_evaluacion)]

    def exportar_claves_excel(self, id_evaluacion: int) -> bytes:
        return claves_a_xlsx(self.exportar_claves(id_evaluacion))

    def generar_clave_aleatoria(self) -> str:
        """Paso 39: 8 caracteres, con letras y dígitos."""
        while True:
            clave = "".join(secrets.choice(_LETRAS + _DIGITOS) for _ in range(LARGO_CLAVE))
            if any(ch in _LETRAS for ch in clave) and any(ch in _DIGITOS for ch in clave):
                return clave

    def tiene_cuestionario_activo(self, nro_candidato: str) -> bool:
        return self.cuestionario_dao.obtener_activo_o_en_proceso(nro_candidato) is not None

    # ---------------- Pendientes ----------------
    def registrar_respuesta_bloque(self, bloque): pendiente("CU026 paso 37")
    def calcular_resultados_cuestionario(self, cuestionario): pendiente("CU026 paso 44")
    def emitir_reporte_comparativo(self, candidato, puesto): pendiente("CU027")
    def generar_orden_merito(self, puesto, evaluacion_seleccionada): pendiente("CU028 paso 21")
    def exportar_resultados(self, criterios): pendiente("CU007")
    def obtener_cuestionario_para_completar(self, candidato): pendiente("CU026 paso 2")
    def armar_cuestionario(self, cuestionario): pendiente("CU026 paso 16 (2 preguntas al azar por factor)")
    def obtener_bloque_pendiente(self, cuestionario): pendiente("CU026 paso 32")

    # ---------------- Internos ----------------
    def _obtener_puesto(self, codigo: str):
        puesto = self.puesto_dao.obtener((codigo or "").strip())
        if puesto is None or puesto.eliminado:
            raise EntidadNoEncontrada("El puesto no existe.")
        return puesto

    @staticmethod
    def _clave_dto(candidato: Candidato, cuestionario: Cuestionario) -> CandidatoClaveDTO:
        return CandidatoClaveDTO(
            nro_candidato=candidato.nro_candidato,
            apellido=candidato.apellido,
            nombre=candidato.nombre,
            tipo_documento=candidato.tipo_documento,
            nro_documento=candidato.nro_documento,
            clave_ingreso=cuestionario.clave_ingreso,
        )
