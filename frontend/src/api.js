const FALLBACK = "No se pudo completar la operación. Intente nuevamente.";

async function post(path, body) {
  let res;
  try {
    res = await fetch(`/api/auth${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
  } catch {
    throw new Error("No se pudo conectar con el servidor.");
  }
  const data = await res.json().catch(() => null);
  if (!res.ok) throw new Error(typeof data?.detail === "string" ? data.detail : FALLBACK);
  return data;
}

export const loginConsultor = (username, password) => post("/consultor", { username, password });

export const loginCandidato = (tipoDocumento, nroDocumento, clave) =>
  post("/candidato", { tipo_documento: tipoDocumento, nro_documento: nroDocumento, clave });
