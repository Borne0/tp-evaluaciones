import hmac

from sqlalchemy import select

from ..entidades.estados import EstadoCuestionario
from ..entidades.models import Candidato, Cuestionario
from ..pendiente import pendiente
from .base import BaseDAO


class CuestionarioDAO(BaseDAO):
    # ---- CU001
    def obtener_por_clave(self, tipo_documento: str, nro_documento: str, clave_ingreso: str) -> Cuestionario | None:
        """Cuestionario activo o en proceso del candidato cuya clave coincide (CU001 paso 3.A.2)."""
        stmt = (
            select(Cuestionario)
            .join(Candidato, Cuestionario.candidato_nro_candidato == Candidato.nro_candidato)
            .where(
                Candidato.tipo_documento == tipo_documento,
                Candidato.nro_documento == nro_documento,
                Candidato.eliminado.is_(False),
                Cuestionario.estado.in_(EstadoCuestionario.ABIERTOS),
            )
        )
        for c in self.db.scalars(stmt):
            if hmac.compare_digest(c.clave_ingreso.encode(), clave_ingreso.encode()):
                return c
        return None

    # ---- Pendientes (diagrama de clases)
    def obtener_activo_o_en_proceso(self, nro_candidato: str) -> Cuestionario | None:
        """Cuestionario activo o en proceso del candidato (CU005 / CU025 / CU026)."""
        return self.db.scalar(
            select(Cuestionario)
            .where(
                Cuestionario.candidato_nro_candidato == nro_candidato,
                Cuestionario.estado.in_(EstadoCuestionario.ABIERTOS),
            )
            .limit(1)
        )
    def actualizar_estado(self, cuestionario, nuevo_estado): pendiente("CU026")
    def guardar_bloque_respuestas(self, cuestionario, respuestas): pendiente("CU026")
    def buscar_vencidos(self): pendiente("CU032")
    def buscar_resultados(self, criterios): pendiente("CU007")

    # ---- Pendientes (diagramas de secuencia)
    def insertar(self, cuestionario: Cuestionario) -> None:
        """CU025: alta del cuestionario de un candidato dentro de una evaluación."""
        self.db.add(cuestionario)
        self.db.flush()

    def buscar_por_evaluacion(self, id_evaluacion: int) -> list[Cuestionario]:
        """CU025 (exportarClaves): cuestionarios de la evaluación, ordenados por apellido y nombre."""
        stmt = (
            select(Cuestionario)
            .join(Candidato, Cuestionario.candidato_nro_candidato == Candidato.nro_candidato)
            .where(Cuestionario.evaluacion_id == id_evaluacion)
            .order_by(Candidato.apellido, Candidato.nombre, Candidato.nro_candidato)
        )
        return list(self.db.scalars(stmt))

    def guardar_estructura(self, cuestionario, bloques, fecha_inicio): pendiente("CU026")
    def obtener_bloque_pendiente(self, cuestionario): pendiente("CU026")
    def guardar_resultados(self, cuestionario, puntajes_factor, puntajes_competencia): pendiente("CU026")
    def contar_completos_por_puesto(self, puesto): pendiente("CU028")
    def buscar_completos_por_evaluaciones(self, evaluaciones): pendiente("CU028")
    def buscar_no_completos_por_evaluaciones(self, evaluaciones): pendiente("CU028")
    def obtener_puntajes_competencia(self, cuestionario): pendiente("CU028")
