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
  if (body !== undefined) headers["Content-Type"] = "application/json";
  if (auth) headers.Authorization = `Bearer ${token()}`;
  let res;
  try {
    res = await fetch(url, { method, headers, body: body === undefined ? undefined : JSON.stringify(body) });
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
