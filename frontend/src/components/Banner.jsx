// Banner de los wireframes: recuadro con logo (placeholder) + título, separado del contenido por una línea.
export default function Banner({ title }) {
  return (
    <header className="banner">
      <div className="banner__logo" aria-hidden="true">
        <svg viewBox="0 0 24 24" fill="none" strokeWidth="2" strokeLinecap="round">
          <path d="M4 4l16 16M20 4L4 20" />
        </svg>
      </div>
      <h1 className="banner__title">{title}</h1>
    </header>
  );
}
