import { useEffect, useRef, useState } from "react";
import { ApiError } from "../api.js";

const TIPOS_DOC = ["DNI", "LE", "LC", "PP"];
export const CANDIDATO_VACIO = {
  nro_candidato: "",
  tipo_documento: "DNI",
  nro_documento: "",
  apellido: "",
  nombre: "",
  fecha_nacimiento: "",
  genero: "",
  nacionalidad: "",
  email: "",
  escolaridad: "",
};

const upper = (v) => v.toUpperCase();
const alnumUpper = (v) => v.replace(/[^a-zA-Z0-9]/g, "").toUpperCase();

const REQUERIDOS = [
  ["nro_candidato", "Número de candidato"],
  ["nro_documento", "Número de documento"],
  ["apellido", "Apellido"],
  ["nombre", "Nombre"],
];

// Formulario compartido por CU003 (alta) y CU004 (modificación). El número de candidato solo se edita en el alta.
export default function CandidatoForm({ inicial = CANDIDATO_VACIO, edicion = false, onSubmit, onCancel }) {
  const [form, setForm] = useState({ ...CANDIDATO_VACIO, ...inicial });
  const [errores, setErrores] = useState([]);
  const [loading, setLoading] = useState(false);
  const firstField = useRef(null);

  useEffect(() => {
    firstField.current?.focus();
  }, []);

  const set = (field, transform = (v) => v) => (e) => setForm((f) => ({ ...f, [field]: transform(e.target.value) }));

  async function submit(e) {
    e.preventDefault();
    if (loading) return;
    const faltantes = REQUERIDOS.filter(([k]) => !form[k].trim()).map(([, label]) => label);
    if (faltantes.length) {
      setErrores([`Falta ingresar: ${faltantes.join(", ")}.`]); // se detallan TODAS las omisiones
      return;
    }
    setErrores([]);
    setLoading(true);
    try {
      await onSubmit({ ...form, fecha_nacimiento: form.fecha_nacimiento || null });
    } catch (err) {
      setErrores(err instanceof ApiError && err.errores.length ? err.errores : [err.message]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <form className="form" onSubmit={submit} autoComplete="off" noValidate>
      <div className="form-grid">
        <label className="field">
          <span>Número de candidato</span>
          <input ref={edicion ? null : firstField} value={form.nro_candidato} onChange={set("nro_candidato", alnumUpper)} maxLength={20} readOnly={edicion} disabled={edicion} placeholder="Ingresar" />
        </label>
        <label className="field">
          <span>Tipo de documento</span>
          <select value={form.tipo_documento} onChange={set("tipo_documento")}>
            {TIPOS_DOC.map((t) => (
              <option key={t}>{t}</option>
            ))}
          </select>
        </label>
        <label className="field">
          <span>Número de documento</span>
          <input ref={edicion ? firstField : null} value={form.nro_documento} onChange={set("nro_documento", alnumUpper)} maxLength={15} spellCheck={false} placeholder="Ingresar" />
        </label>
        <label className="field">
          <span>Apellido</span>
          <input value={form.apellido} onChange={set("apellido", upper)} maxLength={100} spellCheck={false} placeholder="Ingresar" />
        </label>
        <label className="field">
          <span>Nombre</span>
          <input value={form.nombre} onChange={set("nombre", upper)} maxLength={100} spellCheck={false} placeholder="Ingresar" />
        </label>
        <label className="field">
          <span>Fecha de nacimiento</span>
          <input type="date" value={form.fecha_nacimiento || ""} onChange={set("fecha_nacimiento")} max={new Date().toISOString().slice(0, 10)} />
        </label>
        <label className="field">
          <span>Género</span>
          <select value={form.genero || ""} onChange={set("genero")}>
            <option value="">Seleccionar</option>
            <option value="H">H</option>
            <option value="M">M</option>
          </select>
        </label>
        <label className="field">
          <span>Nacionalidad</span>
          <input value={form.nacionalidad || ""} onChange={set("nacionalidad", upper)} maxLength={50} placeholder="Ingresar" />
        </label>
        <label className="field">
          <span>Email</span>
          <input type="email" value={form.email || ""} onChange={set("email")} maxLength={150} spellCheck={false} placeholder="Ingresar" />
        </label>
        <label className="field">
          <span>Escolaridad</span>
          <input value={form.escolaridad || ""} onChange={set("escolaridad", upper)} maxLength={100} placeholder="Ingresar" />
        </label>
      </div>

      {errores.length > 0 && (
        <div className="form-errors" role="alert">
          <strong>No se pudo guardar:</strong>
          <ul>
            {errores.map((m) => (
              <li key={m}>{m}</li>
            ))}
          </ul>
        </div>
      )}

      <div className="actions">
        <button type="button" className="btn btn--secondary" onClick={onCancel}>
          Cancelar
        </button>
        <button type="submit" className="btn btn--primary" disabled={loading}>
          {loading ? "Guardando…" : "Aceptar"}
        </button>
      </div>
    </form>
  );
}
