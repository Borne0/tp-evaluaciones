import { useEffect, useRef } from "react";

// Mensaje informativo con un único botón "Aceptar" (el ErrorDialog queda para los errores).
export default function MessageDialog({ title = "Información", message, onClose }) {
  const btn = useRef(null);

  useEffect(() => {
    btn.current?.focus();
    const onKey = (e) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  return (
    <div className="overlay">
      <div className="dialog dialog--info" role="alertdialog" aria-modal="true" aria-labelledby="msg-title" aria-describedby="msg-text">
        <h2 id="msg-title">{title}</h2>
        <p id="msg-text">{message}</p>
        <button ref={btn} type="button" className="btn btn--primary" onClick={onClose}>
          Aceptar
        </button>
      </div>
    </div>
  );
}
