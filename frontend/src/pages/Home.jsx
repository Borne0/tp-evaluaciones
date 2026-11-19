import { useState } from "react";
import Banner from "../components/Banner.jsx";
import Candidatos from "./Candidatos.jsx";

// Placeholder de la pantalla principal; cada opción se habilitará al implementar su CU.
const OPCIONES_CONSULTOR = [
  "Candidatos",
  "Puestos",
  "Competencias",
  "Factores",
  "Preguntas",
  "Opciones de respuesta",
  "Evaluar candidatos",
  "Importar candidatos",
  "Exportar resultados",
  "Reporte comparativo",
  "Orden de mérito",
];

// Opciones ya implementadas; el resto se habilita al implementar su CU.
const OPCIONES_HABILITADAS = ["Candidatos"];

export default function Home({ session, onLogout }) {
  const esConsultor = session.perfil === "CONSULTOR";
  const [screen, setScreen] = useState(null); // null = menú principal

  if (esConsultor && screen === "Candidatos") return <Candidatos onSalir={() => setScreen(null)} />;

  return (
    <div className="page">
      <Banner title={esConsultor ? "Menú principal" : "Cuestionario"} />

      <main className="main">
        <section className="panel panel--wide">
          <h2>Bienvenido, {session.nombre}</h2>
          {esConsultor ? (
            <>
              <p className="hint">Opciones disponibles para el perfil Consultor.</p>
              <div className="menu">
                {OPCIONES_CONSULTOR.map((o) => (
                  <button key={o} type="button" className="btn btn--secondary" disabled={!OPCIONES_HABILITADAS.includes(o)} onClick={() => setScreen(o)}>
                    {o}
                  </button>
                ))}
              </div>
            </>
          ) : (
            <>
              <p className="hint">Tiene un cuestionario pendiente.</p>
              <button type="button" className="btn btn--primary" disabled>
                Comenzar cuestionario
              </button>
            </>
          )}
        </section>
      </main>

      <footer className="footer">
        <button type="button" className="btn btn--secondary" onClick={onLogout}>
          Salir
        </button>
      </footer>
    </div>
  );
}
