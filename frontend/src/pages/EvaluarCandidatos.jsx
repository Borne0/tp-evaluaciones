import { useEffect, useMemo, useState } from "react";
import Banner from "../components/Banner.jsx";
import ClavesDialog from "../components/ClavesDialog.jsx";
import ErrorDialog from "../components/ErrorDialog.jsx";
import MessageDialog from "../components/MessageDialog.jsx";
import {
  buscarCandidatos, buscarPuestos, competenciasNoEvaluables, crearEvaluacion, descargarClaves,
  mensajeError, nombreArchivoClaves, opcionesPuestos,
} from "../api.js";

// CU025 – Evaluar candidatos. Una sola pantalla con los tres pasos del wireframe:
// 1. Buscar puesto / función   2. Resultados de puestos   3. Seleccionar candidatos a evaluar
export default function EvaluarCandidatos({ onSalir }) {
  const [opciones, setOpciones] = useState({ nombres: [], empresas: [] });
  const [candidatos, setCandidatos] = useState([]);
  const [filtro, setFiltro] = useState({ nombre_puesto: "", empresa: "" });
  const [puestos, setPuestos] = useState(null); // null = todavía no se buscó
  const [puestoSel, setPuestoSel] = useState(null); // código del puesto elegido
  const [seleccion, setSeleccion] = useState(() => new Set()); // nro_candidato
  const [textoCandidatos, setTextoCandidatos] = useState("");
  const [buscando, setBuscando] = useState(false);
  const [verificando, setVerificando] = useState(false);
  const [evaluando, setEvaluando] = useState(false);
  const [exportando, setExportando] = useState(false);
  const [error, setError] = useState(null); // { message, salir }
  const [paso, setPaso] = useState(null); // null | "exito" | "claves"
  const [creada, setCreada] = useState(null);

  const fallo = (err, salir = false) => setError({ message: mensajeError(err), salir });

  useEffect(() => {
    Promise.all([opcionesPuestos(), buscarCandidatos({})])
      .then(([o, c]) => {
        setOpciones(o);
        setCandidatos(c);
      })
      .catch((err) => fallo(err));
  }, []);

  const puesto = puestos?.find((p) => p.codigo === puestoSel);

  const visibles = useMemo(() => {
    const t = textoCandidatos.trim().toUpperCase();
    if (!t) return candidatos;
    return candidatos.filter((c) => [c.apellido, c.nombre, c.nro_candidato, c.nro_documento].some((v) => v?.toUpperCase().includes(t)));
  }, [candidatos, textoCandidatos]);

  // ---- Paso 1: buscar puesto
  async function buscar(e) {
    e.preventDefault();
    if (!filtro.nombre_puesto || !filtro.empresa) {
      return setError({ message: "Debe seleccionar el nombre del puesto y la empresa." });
    }
    setBuscando(true);
    try {
      setPuestos(await buscarPuestos(filtro));
      setPuestoSel(null);
    } catch (err) {
      fallo(err);
    } finally {
      setBuscando(false);
    }
  }

  // ---- Paso 2: elegir puesto; el sistema valida que sus competencias sean evaluables
  async function elegirPuesto(codigo) {
    if (verificando || codigo === puestoSel) return;
    setPuestoSel(codigo);
    setVerificando(true);
    try {
      await competenciasNoEvaluables(codigo); // lanza 409 con los nombres si hay competencias no evaluables
    } catch (err) {
      setPuestoSel(null);
      fallo(err, err.status === 409); // 9.A: Aceptar finaliza el CU
    } finally {
      setVerificando(false);
    }
  }

  // ---- Paso 3: selección de candidatos
  const alternar = (nro) =>
    setSeleccion((s) => {
      const nuevo = new Set(s);
      nuevo.has(nro) ? nuevo.delete(nro) : nuevo.add(nro);
      return nuevo;
    });
  const seleccionarTodos = () => setSeleccion((s) => new Set([...s, ...visibles.map((c) => c.nro_candidato)]));
  const limpiarSeleccion = () => setSeleccion(new Set());

  // ---- Evaluar
  async function evaluar() {
    const faltan = [];
    if (!puestoSel) faltan.push("Debe seleccionar un puesto / función.");
    if (seleccion.size === 0) faltan.push("Debe seleccionar al menos un candidato para evaluar.");
    if (faltan.length) return setError({ message: faltan.join("\n") });

    setEvaluando(true);
    try {
      setCreada(await crearEvaluacion(puestoSel, [...seleccion]));
      setPaso("exito");
    } catch (err) {
      fallo(err); // 6.A / 9.A: se informa y se vuelve a la selección
    } finally {
      setEvaluando(false);
    }
  }

  async function exportar() {
    setExportando(true);
    try {
      await descargarClaves(creada.id_evaluacion, nombreArchivoClaves(creada.nombre_puesto));
      onSalir();
    } catch (err) {
      fallo(err);
    } finally {
      setExportando(false);
    }
  }

  const cerrarError = () => {
    const salir = error?.salir;
    setError(null);
    if (salir) onSalir();
  };

  return (
    <div className="page">
      <Banner title="Evaluar candidatos" />

      <main className="main">
        <section className="panel panel--eval">
          <h2 className="step">1. Buscar puesto / función</h2>
          <form className="eval-search" onSubmit={buscar} autoComplete="off">
            <label className="field">
              <span>Nombre del puesto <b aria-hidden="true">*</b></span>
              <select value={filtro.nombre_puesto} onChange={(e) => setFiltro((f) => ({ ...f, nombre_puesto: e.target.value }))} required>
                <option value="">Seleccione</option>
                {opciones.nombres.map((n) => <option key={n}>{n}</option>)}
              </select>
            </label>
            <label className="field">
              <span>Empresa <b aria-hidden="true">*</b></span>
              <select value={filtro.empresa} onChange={(e) => setFiltro((f) => ({ ...f, empresa: e.target.value }))} required>
                <option value="">Seleccione</option>
                {opciones.empresas.map((n) => <option key={n}>{n}</option>)}
              </select>
            </label>
            <button type="submit" className="btn btn--secondary" disabled={buscando}>
              {buscando ? "Buscando…" : "Buscar"}
            </button>
          </form>

          <h2 className="step">2. Resultados de puestos</h2>
          {puestos === null ? (
            <p className="hint hint--tight">Elija un puesto y una empresa y presione Buscar.</p>
          ) : puestos.length === 0 ? (
            <p className="hint hint--tight">No se encontraron puestos con los criterios ingresados.</p>
          ) : (
            <div className="table-wrap">
              <table className="table">
                <thead>
                  <tr>
                    <th>Código</th>
                    <th>Puesto / Función</th>
                    <th>Empresa</th>
                    <th>Descripción</th>
                  </tr>
                </thead>
                <tbody>
                  {puestos.map((p) => (
                    <tr
                      key={p.codigo}
                      tabIndex={0}
                      aria-selected={p.codigo === puestoSel}
                      onClick={() => elegirPuesto(p.codigo)}
                      onKeyDown={(e) => (e.key === "Enter" || e.key === " ") && (e.preventDefault(), elegirPuesto(p.codigo))}
                    >
                      <td>{p.codigo}</td>
                      <td>{p.nombre_puesto}</td>
                      <td>{p.empresa}</td>
                      <td>{p.descripcion}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
          {puesto && (
            <p className="competencias">
              <strong>Competencias requeridas (ponderación):</strong>{" "}
              {puesto.caracteristicas.map((c) => `${c.nombre_competencia} (${c.ponderacion_minima_requerida})`).join(" · ")}
            </p>
          )}

          <div className="step step--row">
            <h2>3. Seleccionar candidatos a evaluar</h2>
            <input
              type="search"
              className="filter-input"
              placeholder="Filtrar candidatos"
              aria-label="Filtrar candidatos por apellido, nombre, número o documento"
              value={textoCandidatos}
              onChange={(e) => setTextoCandidatos(e.target.value)}
            />
          </div>
          {candidatos.length === 0 ? (
            <p className="hint hint--tight">No hay candidatos disponibles.</p>
          ) : (
            <div className="table-wrap">
              <table className="table table--check">
                <thead>
                  <tr>
                    <th aria-label="Seleccionar" />
                    <th>Candidato</th>
                    <th>Documento</th>
                    <th>Email</th>
                  </tr>
                </thead>
                <tbody>
                  {visibles.map((c) => (
                    <tr key={c.nro_candidato} data-checked={seleccion.has(c.nro_candidato)}>
                      <td>
                        <input
                          type="checkbox"
                          checked={seleccion.has(c.nro_candidato)}
                          onChange={() => alternar(c.nro_candidato)}
                          aria-label={`Seleccionar ${c.apellido} ${c.nombre}`}
                        />
                      </td>
                      <td>{c.apellido} {c.nombre}</td>
                      <td>{c.tipo_documento} {c.nro_documento}</td>
                      <td>{c.email}</td>
                    </tr>
                  ))}
                  {visibles.length === 0 && (
                    <tr><td colSpan={4} className="empty-row">Ningún candidato coincide con el filtro.</td></tr>
                  )}
                </tbody>
              </table>
            </div>
          )}
          <div className="select-links">
            <button type="button" className="link-btn" onClick={seleccionarTodos}>Seleccionar todos</button>
            <span aria-hidden="true">|</span>
            <button type="button" className="link-btn" onClick={limpiarSeleccion}>Limpiar selección</button>
            <span className="select-links__count">{seleccion.size} seleccionado(s)</span>
          </div>
        </section>
      </main>

      <footer className="footer footer--actions">
        <button type="button" className="btn btn--secondary" onClick={onSalir} disabled={evaluando}>
          Cancelar
        </button>
        <button type="button" className="btn btn--primary" onClick={evaluar} disabled={evaluando || verificando}>
          {evaluando ? "Evaluando…" : "Evaluar"}
        </button>
      </footer>

      {paso === "exito" && (
        <MessageDialog
          title="¡ÉXITO!"
          message={"La evaluación de candidatos se ha iniciado correctamente.\nSe generaron los cuestionarios para los candidatos seleccionados."}
          onClose={() => setPaso("claves")}
        />
      )}
      {paso === "claves" && <ClavesDialog claves={creada.claves} exportando={exportando} onSi={exportar} onNo={onSalir} />}
      {error && <ErrorDialog message={error.message} onClose={cerrarError} />}
    </div>
  );
}
