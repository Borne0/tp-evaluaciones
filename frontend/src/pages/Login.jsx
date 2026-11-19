import { useEffect, useRef, useState } from "react";
import Banner from "../components/Banner.jsx";
import ErrorDialog from "../components/ErrorDialog.jsx";
import { loginCandidato, loginConsultor } from "../api.js";

const TIPOS_DOC = ["DNI", "LE", "LC", "PP"];
const EMPTY = { username: "", password: "", tipoDocumento: "DNI", nroDocumento: "", clave: "" };

const upper = (v) => v.toUpperCase();
const alnumUpper = (v) => v.replace(/[^a-zA-Z0-9]/g, "").toUpperCase();

export default function Login({ onLogin }) {
  const [mode, setMode] = useState(null); // null | "consultor" | "candidato"
  const [form, setForm] = useState(EMPTY);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const firstField = useRef(null);

  // Foco en el primer campo al elegir tipo de acceso y al cerrar el error
  useEffect(() => {
    if (!error) firstField.current?.focus();
  }, [mode, error]);

  const set = (field, transform = (v) => v) => (e) =>
    setForm((f) => ({ ...f, [field]: transform(e.target.value) }));

  const selectMode = (next) => {
    setMode(next);
    setForm(EMPTY);
    setError(null);
  };

  const complete =
    mode === "consultor" ? form.username && form.password : mode === "candidato" ? form.nroDocumento && form.clave : false;

  async function submit(e) {
    e.preventDefault();
    if (!complete || loading) return;
    setLoading(true);
    try {
      const session =
        mode === "consultor"
          ? await loginConsultor(form.username, form.password)
          : await loginCandidato(form.tipoDocumento, form.nroDocumento, form.clave);
      onLogin(session);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  const closeError = () => {
    setError(null);
    setForm(EMPTY); // el sistema blanquea los campos
  };

  const salir = () => {
    window.close(); // solo funciona si la pestaña la abrió un script
    selectMode(null);
  };

  return (
    <div className="page">
      <Banner title="Capit@l Humano" />

      <main className="main">
        <section className="panel">
          <h2>Seleccione el tipo de acceso</h2>
          <p className="hint">Elija cómo desea ingresar al sistema.</p>

          <div className="access" role="radiogroup" aria-label="Tipo de acceso">
            <button type="button" role="radio" aria-checked={mode === "consultor"} className="access__option" onClick={() => selectMode("consultor")}>
              <strong>Ingresar como usuario consultor</strong>
              <span>Gestión y evaluaciones</span>
            </button>
            <button type="button" role="radio" aria-checked={mode === "candidato"} className="access__option" onClick={() => selectMode("candidato")}>
              <strong>Realizar cuestionario</strong>
              <span>Acceso para candidatos</span>
            </button>
          </div>

          {mode && (
            <form className="form" onSubmit={submit} autoComplete="off" noValidate>
              {mode === "consultor" ? (
                <>
                  <label className="field">
                    <span>Nombre de usuario</span>
                    <input ref={firstField} value={form.username} onChange={set("username", upper)} maxLength={15} autoCapitalize="characters" spellCheck={false} autoComplete="username" placeholder="Ingresar" />
                  </label>
                  <label className="field">
                    <span>Contraseña</span>
                    <input type="password" value={form.password} onChange={set("password")} maxLength={20} autoComplete="current-password" placeholder="Ingresar" />
                  </label>
                </>
              ) : (
                <>
                  <label className="field">
                    <span>Tipo de documento</span>
                    <select ref={firstField} value={form.tipoDocumento} onChange={set("tipoDocumento")}>
                      {TIPOS_DOC.map((t) => (
                        <option key={t}>{t}</option>
                      ))}
                    </select>
                  </label>
                  <label className="field">
                    <span>Número de documento</span>
                    <input value={form.nroDocumento} onChange={set("nroDocumento", alnumUpper)} maxLength={15} spellCheck={false} placeholder="Ingresar" />
                  </label>
                  <label className="field">
                    <span>Clave</span>
                    <input type="password" value={form.clave} onChange={set("clave")} maxLength={8} autoComplete="off" placeholder="Ingresar" />
                  </label>
                </>
              )}

              <button type="submit" className="btn btn--primary" disabled={!complete || loading}>
                {loading ? "Verificando…" : "Ingresar"}
              </button>
            </form>
          )}
        </section>
      </main>

      <footer className="footer">
        <button type="button" className="btn btn--secondary" onClick={salir}>
          Salir
        </button>
      </footer>

      {error && <ErrorDialog message={error} onClose={closeError} />}
    </div>
  );
}
