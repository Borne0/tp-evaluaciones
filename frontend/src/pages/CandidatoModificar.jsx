import { useEffect, useState } from "react";
import Banner from "../components/Banner.jsx";
import CandidatoForm from "../components/CandidatoForm.jsx";
import ErrorDialog from "../components/ErrorDialog.jsx";
import MessageDialog from "../components/MessageDialog.jsx";
import { modificarCandidato, obtenerCandidato } from "../api.js";

// CU004 – Modificar candidato
export default function CandidatoModificar({ nroCandidato, onFinish }) {
  const [candidato, setCandidato] = useState(null);
  const [error, setError] = useState(null);
  const [exito, setExito] = useState(false);

  useEffect(() => {
    obtenerCandidato(nroCandidato).then(setCandidato).catch((e) => setError(e.message));
  }, [nroCandidato]);

  const guardar = async (datos) => {
    await modificarCandidato(nroCandidato, datos);
    setExito(true);
  };

  return (
    <div className="page">
      <Banner title="Modificar candidato" />

      <main className="main">
        <section className="panel panel--form">
          <h2>Datos del candidato</h2>
          <p className="hint">El número de candidato no se puede modificar.</p>
          {candidato && <CandidatoForm inicial={candidato} edicion onSubmit={guardar} onCancel={onFinish} />}
        </section>
      </main>

      {exito && <MessageDialog message="La operación ha culminado con éxito" onClose={onFinish} />}
      {error && <ErrorDialog message={error} onClose={onFinish} />}
    </div>
  );
}
