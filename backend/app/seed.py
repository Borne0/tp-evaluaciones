"""Datos de prueba: python -m app.seed"""
from datetime import date

from sqlalchemy import select

from .entidades import models as m
from .entidades.estados import EstadoCuestionario, EstadoEvaluacion, TipoCompetencia
from .infraestructura.database import Base, SessionLocal, engine

Base.metadata.create_all(engine)

with SessionLocal() as db:
    if db.scalar(select(m.Consultor).where(m.Consultor.username == "CONSULTOR")):
        print("Los datos de prueba ya existen")
        raise SystemExit

    db.add(m.Consultor(legajo="L0001", username="CONSULTOR"))
    db.add(m.Competencia(codigo="COMP01", nombre="GESTION DE PROYECTOS", descripcion="Competencia técnica", tipo=TipoCompetencia.TECNICA))
    db.add(m.Puesto(codigo="P001", nombre_puesto="DESARROLLADOR BACKEND", descripcion="Servicios y APIs", empresa="MERCADOLIBRE"))
    db.add(m.CaracteristicaPuesto(puesto_codigo="P001", competencia_codigo="COMP01", ponderacion_minima_requerida=6))
    db.add(m.Candidato(nro_candidato="C0001", tipo_documento="DNI", nro_documento="12345678", apellido="PEREZ", nombre="JUAN"))
    evaluacion = m.Evaluacion(fecha_creacion=date.today(), estado=EstadoEvaluacion.ACTIVA, puesto_codigo="P001")
    evaluacion.cuestionarios.append(
        m.Cuestionario(estado=EstadoCuestionario.ACTIVO, clave_ingreso="AB12CD34", candidato_nro_candidato="C0001")
    )
    db.add(evaluacion)
    db.commit()
    print("Listo. Consultor: CONSULTOR / consultor123 (mock). Candidato: DNI 12345678 / clave AB12CD34")
