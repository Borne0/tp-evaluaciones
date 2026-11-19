# Arquitectura y mapa de las entregas

## Capas (diagrama de despliegue → paquetes `backend/app`)
| Despliegue | Código |
|---|---|
| Capa de Interfaz (páginas / controladores web) | `interfaz/` (routers FastAPI) + `frontend/` (React) |
| Capa de Negocio (Gestores) | `gestores/` |
| Entidades (DER / diagrama de clases) | `entidades/models.py`, `entidades/estados.py` |
| Capa de Datos (DAOs) | `dao/` (la sesión se inyecta; el commit lo hace el Gestor) |
| DTO | `dto/` |
| Servidor LDAP (389/636) | `infraestructura/ldap_client.py` (`LDAP_SERVER=ldaps://…:636`) |
| Servicio de IA (HTTPS/REST) | `infraestructura/ia_client.py` (CU021/033 y CU009) |
| Sistema de Candidatos y CV (HTTPS/REST) | `infraestructura/sistema_candidatos_client.py` (CU006/007) |
| Impresora (IPP) | `infraestructura/impresora.py` (CU028) |
| BD (JDBC en el diseño) | PostgreSQL vía psycopg (`infraestructura/database.py`) |

HTTPS: en producción se termina TLS en un proxy inverso (nginx/Caddy) delante de FastAPI y del frontend.

## Estado
- **Implementado:** CU001 (`GestorAutenticacion`, `ConsultorDAO`, `CuestionarioDAO.obtener_por_clave`), todas las entidades del DER, todos los DTO.
- **Esqueletos:** gestores y DAOs del diagrama de clases con `pendiente("CUxxx")` en cada método.

## Diferencias entre las entregas (para resolver en el próximo ajuste)
1. **Baja lógica**: el DER no tiene `eliminado` en Puesto, Competencia, Factor, Pregunta ni OpcionRespuesta, pero los CU011/015/019/023/031 la exigen → agregado.
2. **`Cuestionario.fechaCreacion`**: el diagrama de secuencia del CU026 lo usa (tiempo máximo en estado Activo) y no está en el DER → agregado.
3. **CU026** usa `BloqueCuestionario` y `RepositorioConfiguracionDAO`, que no están en el diagrama de clases (el DER maneja los bloques con `PREGUNTA_CUESTIONARIO.numeroBloque`).
4. **`GestorAutenticacion`** (CU001) no figura en el diagrama de clases.
5. **`claveIngreso`** se guarda en texto plano porque `exportarClaves` (CU025) la lee de la BD para el Excel.
6. Longitudes: CU008 define código de 10 y nombre de 300; CU009 define 50 y 100. Se usó CU009.

## Secuencias para implementar (resumen)
- **CU020**: `GestorPreguntas.buscarPregunta(PreguntaCriteriosDTO)` → `PreguntaDAO.buscar` → `List<PreguntaDTO>`; Nuevo/Modificar/Eliminar navegan a CU021/022/023 y luego actualizan la grilla.
- **CU021**: al elegir Competencia → `GestorFactores.buscarFactor`; Aceptar → `GestorPreguntas.darAltaPregunta(PreguntaDTO)` → `PreguntaDAO.existePregunta(nombre, enunciado, competencia, factor)`; si no existe → `insertar`.
- **CU023**: confirmación → `darBajaPregunta` → `PreguntaDAO.eliminar` (baja lógica) → `RegistroAuditoriaDAO.insertar(fecha, hora, usuario, "BAJA_PREGUNTA", "Pregunta", id)`.
- **CU025**: `buscarCandidato` → por candidato `tieneCuestionarioActivo` → `buscarPuesto` → `validarCompetenciasEvaluables` (factor con ≥ 2 preguntas) → `crearEvaluacion` (Evaluacion "Activa" + un Cuestionario "Activo" con `generarClaveAleatoria()` por candidato) → opcional `exportarClaves` (.xls).
- **CU026**: `obtenerCuestionarioParaCompletar` (+ `obtenerParametros`); Activo → valida `tiempoMaximoActivo` ("Sin Contestar"); En Proceso → valida `tiempoMaximoCuestionario` ("Incompleto"); Aceptar → `armarCuestionario` (2 preguntas al azar por factor, mezcla, bloques) → "En Proceso"; por bloque `registrarRespuestaBloque`; último bloque → `calcularResultadosCuestionario` → "Completo".
- **CU028**: `buscarPuestoConResumen` (candidatos y evaluaciones completas) → `EvaluacionDAO.buscarPorPuesto` → elegir evaluaciones o TODAS → `generarOrdenMerito`: completos y no completos, `obtenerCaracteristicas`, puntajes por competencia vs. mínimo, promedio, orden descendente, resto agrupado por estado → `OrdenDeMeritoDTO` → Imprimir (IPP).
