import { useState } from "react";
import Banner from "../components/Banner.jsx";
import ConfirmDialog from "../components/ConfirmDialog.jsx";
import ErrorDialog from "../components/ErrorDialog.jsx";
import MessageDialog from "../components/MessageDialog.jsx";
import { bajaCandidato, buscarCandidatos, validarBajaCandidato } from "../api.js";
import CandidatoAlta from "./CandidatoAlta.jsx";
import CandidatoModificar from "./CandidatoModificar.jsx";

const FILTROS_VACIOS = { apellido: "", nombre: "", nro_candidato: "" };
const alnumUpper = (v) => v.replace(/[^a-zA-Z0-9]/g, "").toUpperCase();
const upper = (v) => v.toUpperCase();

// CU002 – Gestionar candidatos. Nuevo / Modificar / Eliminar invocan CU003 / CU004 / CU005.
export default function Candidatos({ onSalir }) {
  const [view, setView] = useState("lista"); // "lista" | "alta" | "modificar"
  const [filtros, setFiltros] = useState(FILTROS_VACIOS);
  const [resultados, setResultados] = useState(null); // null = todavía no se buscó
  const [ultimaBusqueda, setUltimaBusqueda] = useState(null);
  const [seleccionado, setSeleccionado] = useState(null); // nro_candidato
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [aEliminar, setAEliminar] = useState(null); // candidato pendiente de confirmar la baja
  const [eliminado, setEliminado] = useState(null); // candidato recién eliminado

  const set = (field, transform) => (e) => setFiltros((f) => ({ ...f, [field]: transform(e.target.value) }));

  async function buscar(criterios) {
    setLoading(true);
    try {
      setResultados(await buscarCandidatos(criterios));
      setUltimaBusqueda(criterios);
      setSeleccionado(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  const onBuscar = (e) => {
    e.preventDefault();
    if (!loading) buscar(filtros);
  };

  // Al volver de Nuevo / Modificar el sistema actualiza la grilla y continúa en el paso de búsqueda
  const volverALista = () => {
    setView("lista");
    if (ultimaBusqueda) buscar(ultimaBusqueda);
  };

  const elegido = resultados?.find((c) => c.nro_candidato === seleccionado);

  async function eliminar() {
    try {
      await validarBajaCandidato(elegido.nro_candidato); // el sistema constata que no esté en uso
      setAEliminar(elegido);
    } catch (err) {
      setError(err.message);
    }
  }

  async function confirmarBaja() {
    const c = aEliminar;
    setAEliminar(null);
    try {
      await bajaCandidato(c.nro_candidato);
      setEliminado(c);
    } catch (err) {
      setError(err.message);
    }
  }

  if (view === "alta") return <CandidatoAlta onFinish={volverALista} />;
  if (view === "modificar") return <CandidatoModificar nroCandidato={seleccionado} onFinish={volverALista} />;

  return (
    <div className="page">
      <Banner title="Gestionar candidatos" />

      <main className="main">
        <section className="panel panel--list">
          <h2>Búsqueda de candidatos</h2>
          <p className="hint">Ingrese uno o más criterios, o deje los campos vacíos para ver todos los candidatos.</p>

          <form className="filters" onSubmit={onBuscar} autoComplete="off">
            <label className="field">
              <span>Número de candidato</span>
              <input value={filtros.nro_candidato} onChange={set("nro_candidato", alnumUpper)} maxLength={20} placeholder="Ingresar" />
            </label>
            <label className="field">
              <span>Apellido</span>
              <input value={filtros.apellido} onChange={set("apellido", upper)} maxLength={100} placeholder="Ingresar" />
            </label>
            <label className="field">
              <span>Nombre</span>
              <input value={filtros.nombre} onChange={set("nombre", upper)} maxLength={100} placeholder="Ingresar" />
            </label>
            <div className="filters__buttons">
              <button type="submit" className="btn btn--primary" disabled={loading}>
                {loading ? "Buscando…" : "Buscar"}
              </button>
              <button type="button" className="btn btn--secondary" onClick={() => setView("alta")}>
                Nuevo
              </button>
            </div>
          </form>

          {resultados && (
            <>
              {resultados.length === 0 ? (
                <p className="hint hint--empty">No se encontraron candidatos con los criterios ingresados.</p>
              ) : (
                <div className="table-wrap">
                  <table className="table">
                    <thead>
                      <tr>
                        <th>Nº candidato</th>
                        <th>Apellido</th>
                        <th>Nombre</th>
                        <th>Tipo doc.</th>
                        <th>Nº documento</th>
                      </tr>
                    </thead>
                    <tbody>
                      {resultados.map((c) => (
                        <tr
                          key={c.nro_candidato}
                          tabIndex={0}
                          aria-selected={c.nro_candidato === seleccionado}
                          onClick={() => setSeleccionado(c.nro_candidato)}
                          onKeyDown={(e) => (e.key === "Enter" || e.key === " ") && (e.preventDefault(), setSeleccionado(c.nro_candidato))}
                        >
                          <td>{c.nro_candidato}</td>
                          <td>{c.apellido}</td>
                          <td>{c.nombre}</td>
                          <td>{c.tipo_documento}</td>
                          <td>{c.nro_documento}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}

              <div className="actions">
                <button type="button" className="btn btn--secondary" disabled={!elegido} onClick={() => setView("modificar")}>
                  Modificar
                </button>
                <button type="button" className="btn btn--secondary" disabled={!elegido} onClick={eliminar}>
                  Eliminar
                </button>
              </div>
            </>
          )}
        </section>
      </main>

      <footer className="footer">
        <button type="button" className="btn btn--secondary" onClick={onSalir}>
          Salir
        </button>
      </footer>

      {aEliminar && (
        <ConfirmDialog
          title="Eliminar candidato"
          message={`Los datos del candidato ${aEliminar.apellido} ${aEliminar.nombre} serán eliminados del sistema`}
          confirmLabel="ELIMINAR"
          cancelLabel="CANCELAR"
          onConfirm={confirmarBaja}
          onCancel={() => setAEliminar(null)}
        />
      )}
      {eliminado && (
        <MessageDialog
          message={`Los datos del candidato ${eliminado.apellido} ${eliminado.nombre} han sido eliminados del sistema.`}
          onClose={() => {
            setEliminado(null);
            buscar(ultimaBusqueda ?? filtros);
          }}
        />
      )}
      {error && <ErrorDialog message={error} onClose={() => setError(null)} />}
    </div>
  );
}
