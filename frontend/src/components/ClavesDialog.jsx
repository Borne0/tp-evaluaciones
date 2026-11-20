import { useEffect, useRef } from "react";

// CU025 pasos 43-44: claves generadas + pregunta de exportación a Excel.
// No se cierra con Escape a propósito: es la única pantalla donde se muestran las claves.
export default function ClavesDialog({ claves, exportando, onSi, onNo }) {
  const btn = useRef(null);
  useEffect(() => btn.current?.focus(), []);

  return (
    <div className="overlay">
      <div className="dialog dialog--info dialog--wide" role="alertdialog" aria-modal="true" aria-labelledby="cl-title" aria-describedby="cl-msg">
        <h2 id="cl-title">Claves de ingreso</h2>
        <p id="cl-msg">¿Desea exportar los candidatos con sus claves a un archivo Excel? Anótelas o expórtelas antes de continuar: no volverán a mostrarse en esta pantalla.</p>

        <div className="table-wrap table-wrap--dialog">
          <table className="table table--static">
            <thead>
              <tr>
                <th>Apellido</th>
                <th>Nombre</th>
                <th>Documento</th>
                <th>Clave</th>
              </tr>
            </thead>
            <tbody>
              {claves.map((c) => (
                <tr key={c.nro_candidato}>
                  <td>{c.apellido}</td>
                  <td>{c.nombre}</td>
                  <td>{c.tipo_documento} {c.nro_documento}</td>
                  <td className="clave">{c.clave_ingreso}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="dialog__actions">
          <button type="button" className="btn btn--secondary" onClick={onNo} disabled={exportando}>
            NO
          </button>
          <button ref={btn} type="button" className="btn btn--primary" onClick={onSi} disabled={exportando}>
            {exportando ? "Exportando…" : "SÍ"}
          </button>
        </div>
      </div>
    </div>
  );
}
