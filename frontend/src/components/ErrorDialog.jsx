import { useEffect, useRef } from "react";

export default function ErrorDialog({ message, onClose }) {
  const btn = useRef(null);

  useEffect(() => {
    btn.current?.focus();
    const onKey = (e) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  return (
    <div className="overlay">
      <div className="dialog" role="alertdialog" aria-modal="true" aria-labelledby="err-title" aria-describedby="err-msg">
        <h2 id="err-title">Error</h2>
        <p id="err-msg">{message}</p>
        <button ref={btn} type="button" className="btn btn--primary" onClick={onClose}>
          Aceptar
        </button>
      </div>
    </div>
  );
}
