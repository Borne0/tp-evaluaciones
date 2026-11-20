import { useRef, useState } from "react";
import Banner from "../components/Banner.jsx";
import ErrorDialog from "../components/ErrorDialog.jsx";
import { importarCandidatos, mensajeError } from "../api.js";

const MAX_BYTES = 10 * 1024 * 1024;

function Resultado({ r, onClose }) {
  const btn = useRef(null);
  return (
    <div className="overlay">
      <div className="dialog dialog--info dialog--wide" role="alertdialog" aria-modal="true" aria-labelledby="imp-title">
        <h2 id="imp-title">Importación finalizada</h2>
        <ul className="stats">
          <li><strong>{r.cantidad_creados}</strong> candidato(s) creado(s)</li>
          <li><strong>{r.cantidad_actualizados}</strong> candidato(s) actualizado(s)</li>
          <li><strong>{r.cantidad_eliminados}</strong> candidato(s) eliminado(s)</li>
        </ul>
        {r.cantidad_omitidos > 0 && (
          <div className="form-errors" role="status">
            {r.cantidad_omitidos} fila(s) no se importaron:
            <ul className="dialog__scroll">
              {r.advertencias.map((a) => <li key={a}>{a}</li>)}
            </ul>
          </div>
        )}
        <div className="dialog__actions">
          <button ref={(el) => { btn.current = el; el?.focus(); }} type="button" className="btn btn--primary" onClick={onClose}>
            Aceptar
          </button>
        </div>
      </div>
    </div>
  );
}

// CU006 – Importar candidatos desde el CSV del sistema de Gestión de Candidatos y CV.
export default function ImportarCandidatos({ onSalir }) {
  const [archivo, setArchivo] = useState(null);
  const [importando, setImportando] = useState(false);
  const [resultado, setResultado] = useState(null);
  const [error, setError] = useState(null);

  function elegir(e) {
    setArchivo(e.target.files?.[0] ?? null);
  }

  async function importar() {
    if (!archivo) return setError("Debe seleccionar el archivo CSV a importar.");
    if (!archivo.name.toLowerCase().endsWith(".csv")) return setError("El archivo debe tener extensión .csv.");
    if (archivo.size > MAX_BYTES) return setError("El archivo supera el tamaño máximo permitido (10 MB).");

    setImportando(true);
    try {
      setResultado(await importarCandidatos(archivo));
    } catch (err) {
      setError(mensajeError(err));
    } finally {
      setImportando(false);
    }
  }

  return (
    <div className="page">
      <Banner title="Importar candidatos" />

      <main className="main">
        <section className="panel panel--form">
          <h2>Seleccione el archivo a importar</h2>
          <p className="hint">
            Archivo CSV separado por punto y coma (;), con los nombres de las columnas en la primera fila: Nro candidato, Apellido, Nombre,
            Nro documento, Tipo documento, Fecha de nacimiento, Género, Nacionalidad, Email, Escolaridad y Eliminado. El Nro de candidato
            identifica a cada candidato: si ya existe se actualiza, y si no, se crea.
          </p>

          <label className="field">
            <span>Archivo CSV</span>
            <input type="file" accept=".csv,text/csv" onChange={elegir} disabled={importando} />
          </label>
          {archivo && <p className="file-info">{archivo.name} · {(archivo.size / 1024).toFixed(1)} KB</p>}

          {importando && (
            <div className="progress" role="progressbar" aria-busy="true" aria-label="Importando candidatos">
              <div className="progress__bar" />
              <span>Importando candidatos…</span>
            </div>
          )}
        </section>
      </main>

      <footer className="footer footer--actions">
        {/* Mientras el servidor procesa el archivo no se puede cancelar: la importación se aplica completa */}
        <button type="button" className="btn btn--secondary" onClick={onSalir} disabled={importando}>
          Cancelar
        </button>
        <button type="button" className="btn btn--primary" onClick={importar} disabled={importando}>
          {importando ? "Importando…" : "Importar"}
        </button>
      </footer>

      {resultado && <Resultado r={resultado} onClose={onSalir} />}
      {error && <ErrorDialog message={error} onClose={() => setError(null)} />}
    </div>
  );
}
