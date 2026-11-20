"""Datos de prueba (idempotente): python -m app.seed"""
from datetime import date

from sqlalchemy import select

from .entidades import models as m
from .entidades.estados import EstadoCuestionario, EstadoEvaluacion, TipoCompetencia
from .infraestructura.database import Base, SessionLocal, engine

Base.metadata.create_all(engine)

OPCION = "VERDADERO-FALSO"

with SessionLocal() as db:
    # Todo lo que tiene clave natural se inserta con merge (no duplica si el seed se corre de nuevo).
    db.merge(m.Consultor(legajo="L0001", username="CONSULTOR"))

    # --- Competencias y factores
    for codigo, nombre, tipo in (
        ("COMP01", "GESTION DE PROYECTOS", TipoCompetencia.TECNICA),
        ("COMP02", "LEALTAD", TipoCompetencia.ACTITUDINAL),
        ("COMP03", "TESTING", TipoCompetencia.TECNICA),
    ):
        db.merge(m.Competencia(codigo=codigo, nombre=nombre, descripcion=f"Competencia {tipo.lower()}", tipo=tipo))
    db.flush()
    for codigo, nombre, orden, comp in (
        ("F01", "GESTION DEL ALCANCE", 1, "COMP01"),
        ("F02", "GESTION DEL TIEMPO", 2, "COMP01"),
        ("F03", "CREDIBILIDAD", 1, "COMP02"),
        ("F04", "PRUEBAS FUNCIONALES", 1, "COMP03"),  # 1 sola pregunta -> COMP03 no es evaluable
    ):
        db.merge(m.Factor(codigo=codigo, nombre=nombre, descripcion=nombre.capitalize(), nro_orden=orden, competencia_codigo=comp))

    # --- Opción de respuesta y preguntas
    db.merge(m.OpcionRespuesta(nombre=OPCION, descripcion="Respuesta verdadera o falsa"))
    db.flush()
    db.merge(m.ItemOpcion(opcion_respuesta_nombre=OPCION, orden=1, descripcion="VERDADERO"))
    db.merge(m.ItemOpcion(opcion_respuesta_nombre=OPCION, orden=2, descripcion="FALSO"))
    db.flush()

    preguntas = (
        ("WBS ALCANCE", "¿LA WBS FORMA PARTE DE LA DEFINICION DEL ALCANCE?", "F01"),
        ("LINEA BASE ALCANCE", "¿AL DEFINIR EL ALCANCE DEBE DEFINIRSE UNA LINEA BASE DE REQUERIMIENTOS?", "F01"),
        ("FIN A COMIENZO", "¿UNA ACTIVIDAD FIN A COMIENZO EMPIEZA CUANDO TERMINA SU PREDECESORA?", "F02"),
        ("VALOR GANADO", "¿EL VALOR GANADO PERMITE PREDECIR EL COSTO FINAL DEL PROYECTO?", "F02"),
        ("CONFIANZA", "¿MIS HECHOS PROFESIONALES DEMUESTRAN QUE SOY DIGNO DE CONFIANZA?", "F03"),
        ("COMPROMISOS", "¿ASUMO TODOS LOS COMPROMISOS QUE CONTRAIGO?", "F03"),
        ("PRUEBA UNICA", "¿UNA PRUEBA FUNCIONAL VERIFICA UN REQUERIMIENTO?", "F04"),
    )
    for nombre, enunciado, factor in preguntas:
        if db.scalar(select(m.Pregunta).where(m.Pregunta.nombre_pregunta == nombre)):
            continue
        pregunta = m.Pregunta(nombre_pregunta=nombre, enunciado=enunciado, factor_codigo=factor, opcion_respuesta_nombre=OPCION)
        db.add(pregunta)
        db.flush()  # asigna id_pregunta (autoincremental: no se fija a mano)
        db.add(m.PonderacionItemPregunta(id_pregunta=pregunta.id_pregunta, nombre_opcion_respuesta=OPCION, orden=1, ponderacion=10))
        db.add(m.PonderacionItemPregunta(id_pregunta=pregunta.id_pregunta, nombre_opcion_respuesta=OPCION, orden=2, ponderacion=0))

    # --- Puestos
    for codigo, nombre, desc, empresa in (
        ("P001", "DESARROLLADOR BACKEND", "Servicios y APIs", "MERCADOLIBRE"),
        ("P002", "ANALISTA FUNCIONAL", "Relevamiento y documentación funcional", "ACCENTURE"),
        ("P003", "QA TESTER", "Testing manual y automatizado", "GLOBANT"),  # su competencia no es evaluable
    ):
        db.merge(m.Puesto(codigo=codigo, nombre_puesto=nombre, descripcion=desc, empresa=empresa))
    db.flush()
    for puesto, comp, minimo in (("P001", "COMP01", 6), ("P001", "COMP02", 5), ("P002", "COMP01", 5), ("P003", "COMP03", 6)):
        db.merge(m.CaracteristicaPuesto(puesto_codigo=puesto, competencia_codigo=comp, ponderacion_minima_requerida=minimo))

    # --- Candidatos
    for nro, doc, ape, nom, gen, email in (
        ("C0001", "12345678", "PEREZ", "JUAN", None, None),
        ("C0002", "23456789", "GOMEZ", "MARIA", "M", "maria.gomez@example.com"),
        ("C0003", "34567890", "LOPEZ", "CARLOS", "H", None),
        ("C0004", "45678901", "FERNANDEZ", "LUCIA", "M", "lucia.fernandez@example.com"),
        ("C0005", "56789012", "RUIZ", "MATIAS", "H", "matias.ruiz@example.com"),
    ):
        if db.get(m.Candidato, nro) is None:
            db.add(m.Candidato(nro_candidato=nro, tipo_documento="DNI", nro_documento=doc, apellido=ape, nombre=nom, genero=gen, email=email))
    db.flush()

    # --- Una evaluación previa: C0001 queda con un cuestionario activo (no se puede evaluar de nuevo)
    if db.scalar(select(m.Cuestionario).where(m.Cuestionario.clave_ingreso == "AB12CD34")) is None:
        evaluacion = m.Evaluacion(fecha_creacion=date.today(), estado=EstadoEvaluacion.ACTIVA, puesto_codigo="P001")
        evaluacion.cuestionarios.append(
            m.Cuestionario(estado=EstadoCuestionario.ACTIVO, clave_ingreso="AB12CD34", candidato_nro_candidato="C0001")
        )
        db.add(evaluacion)

    db.commit()
    print("Listo. Consultor: CONSULTOR / consultor123 (mock). Candidato: DNI 12345678 / clave AB12CD34")
