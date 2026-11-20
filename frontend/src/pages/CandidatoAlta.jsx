import { useState } from "react";
import Banner from "../components/Banner.jsx";
import CandidatoForm from "../components/CandidatoForm.jsx";
import ConfirmDialog from "../components/ConfirmDialog.jsx";
import { altaCandidato } from "../api.js";

// CU003 – Dar de alta candidato
export default function CandidatoAlta({ onFinish }) {
  const [creado, setCreado] = useState(null); // candidato recién creado
  const [formKey, setFormKey] = useState(0); // cambia para volver a presentar el formulario en blanco

  const guardar = async (datos) => setCreado(await altaCandidato(datos));

  return (
    <div className="page">
      <Banner title="Alta de candidato" />

      <main className="main">
        <section className="panel panel--form">
          <h2>Datos del candidato</h2>
          <p className="hint">Complete los datos del nuevo candidato.</p>
          <CandidatoForm key={formKey} onSubmit={guardar} onCancel={onFinish} />
        </section>
      </main>

      {creado && (
        <ConfirmDialog
          title="Candidato creado"
          message={`El candidato ${creado.apellido} ${creado.nombre} se ha creado correctamente ¿Desea cargar otro?`}
          confirmLabel="SI"
          cancelLabel="NO"
          onConfirm={() => {
            setCreado(null);
            setFormKey((k) => k + 1);
          }}
          onCancel={onFinish}
        />
      )}
    </div>
  );
}
