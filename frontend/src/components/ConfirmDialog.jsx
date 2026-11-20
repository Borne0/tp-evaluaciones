import { useEffect, useRef } from "react";

// Diálogo con dos botones (p. ej. "ELIMINAR" / "CANCELAR" o "SI" / "NO"). Escape equivale al botón secundario.
export default function ConfirmDialog({ title = "Confirmar", message, confirmLabel, cancelLabel, onConfirm, onCancel }) {
  const btn = useRef(null);

  useEffect(() => {
    btn.current?.focus();
    const onKey = (e) => e.key === "Escape" && onCancel();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onCancel]);

  return (
    <div className="overlay">
      <div className="dialog dialog--info" role="alertdialog" aria-modal="true" aria-labelledby="cf-title" aria-describedby="cf-msg">
        <h2 id="cf-title">{title}</h2>
        <p id="cf-msg">{message}</p>
        <div className="dialog__actions">
          <button type="button" className="btn btn--secondary" onClick={onCancel}>
            {cancelLabel}
          </button>
          <button ref={btn} type="button" className="btn btn--primary" onClick={onConfirm}>
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}
