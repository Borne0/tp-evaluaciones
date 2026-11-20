const FALLBACK = "No se pudo completar la operación. Intente nuevamente.";
const KEY = "session"; // misma clave que usa App.jsx

// Error de la API: `errores` trae TODAS las omisiones cuando el backend las detalla (alta / modificación).
export class ApiError extends Error {
  constructor(message, errores = [], status = 0) {
    super(message);
    this.errores = errores;
    this.status = status;
  }
}

const token = () => {
  try {
    return JSON.parse(sessionStorage.getItem(KEY))?.token;
  } catch {
    return null;
  }
};

async function call(url, { method = "GET", body, auth = false } = {}) {
  const headers = {};
  const esArchivo = body instanceof FormData; // el navegador completa el Content-Type (multipart)
  if (body !== undefined && !esArchivo) headers["Content-Type"] = "application/json";
  if (auth) headers.Authorization = `Bearer ${token()}`;
  let res;
  try {
    res = await fetch(url, { method, headers, body: body === undefined || esArchivo ? body : JSON.stringify(body) });
  } catch {
    throw new ApiError("No se pudo conectar con el servidor.");
  }
  const data = await res.json().catch(() => null);
  if (!res.ok) {
    if (auth && res.status === 401) {
      // sesión vencida: se vuelve a la pantalla de autenticación
      sessionStorage.removeItem(KEY);
      window.location.reload();
    }
    const detail = data?.detail;
    if (typeof detail === "string") throw new ApiError(detail, [], res.status);
    if (Array.isArray(detail?.errores)) throw new ApiError("Revise los datos ingresados.", detail.errores, res.status);
    throw new ApiError(FALLBACK, [], res.status);
  }
  return data;
}

// ---- CU001
const post = (path, body) => call(`/api/auth${path}`, { method: "POST", body });

export const loginConsultor = (username, password) => post("/consultor", { username, password });

export const loginCandidato = (tipoDocumento, nroDocumento, clave) =>
  post("/candidato", { tipo_documento: tipoDocumento, nro_documento: nroDocumento, clave });

// ---- CU002 a CU005 (candidatos)
const candidato = (nro = "") => `/api/candidatos${nro ? `/${encodeURIComponent(nro)}` : ""}`;

export const buscarCandidatos = (criterios) => {
  const qs = new URLSearchParams();
  Object.entries(criterios).forEach(([k, v]) => v?.trim() && qs.set(k, v.trim()));
  const q = qs.toString();
  return call(`${candidato()}${q ? `?${q}` : ""}`, { auth: true });
};
export const obtenerCandidato = (nro) => call(candidato(nro), { auth: true });
export const altaCandidato = (datos) => call(candidato(), { method: "POST", body: datos, auth: true });
export const modificarCandidato = (nro, datos) => call(candidato(nro), { method: "PUT", body: datos, auth: true });
export const validarBajaCandidato = (nro) => call(`${candidato(nro)}/puede-eliminarse`, { auth: true });
export const bajaCandidato = (nro) => call(candidato(nro), { method: "DELETE", auth: true });

// Texto para mostrar un error: si el backend detalló varias omisiones se muestran todas, una por línea.
export const mensajeError = (err) => (err.errores?.length ? err.errores.join("\n") : err.message);

// ---- CU006 (importar candidatos)
export const importarCandidatos = (archivo) => {
  const datos = new FormData();
  datos.append("archivo", archivo);
  return call(`${candidato()}/importar`, { method: "POST", body: datos, auth: true });
};

// ---- CU025 (evaluar candidatos)
export const opcionesPuestos = () => call("/api/puestos/opciones", { auth: true });

export const buscarPuestos = ({ nombre_puesto, empresa }) => {
  const qs = new URLSearchParams({ nombre_puesto, empresa, exacto: "true" });
  return call(`/api/puestos?${qs}`, { auth: true });
};

export const competenciasNoEvaluables = (codigoPuesto) =>
  call(`/api/evaluaciones/puestos/${encodeURIComponent(codigoPuesto)}/competencias-no-evaluables`, { auth: true });

export const crearEvaluacion = (codigoPuesto, nrosCandidato) =>
  call("/api/evaluaciones", { method: "POST", body: { codigo_puesto: codigoPuesto, nros_candidato: nrosCandidato }, auth: true });

// aaaa-mm-dd-hh-mm-NombreFunción.xlsx
export function nombreArchivoClaves(nombrePuesto, fecha = new Date()) {
  const p = (n) => String(n).padStart(2, "0");
  const base = `${fecha.getFullYear()}-${p(fecha.getMonth() + 1)}-${p(fecha.getDate())}-${p(fecha.getHours())}-${p(fecha.getMinutes())}`;
  const puesto = nombrePuesto.replace(/[\\/:*?"<>|]+/g, "").replace(/\s+/g, " ").trim();
  return `${base}-${puesto}.xlsx`;
}

export async function descargarClaves(idEvaluacion, nombreArchivo) {
  let res;
  try {
    res = await fetch(`/api/evaluaciones/${idEvaluacion}/claves.xlsx`, { headers: { Authorization: `Bearer ${token()}` } });
  } catch {
    throw new ApiError("No se pudo conectar con el servidor.");
  }
  if (!res.ok) throw new ApiError(FALLBACK, [], res.status);
  const url = URL.createObjectURL(await res.blob());
  const a = Object.assign(document.createElement("a"), { href: url, download: nombreArchivo });
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}
