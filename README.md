# TP 2026 – Evaluación de candidatos (Capit@l Humano)

Implementado: **CU001** (autenticar), **CU002–005** (candidatos), **CU006** (importar candidatos) y **CU025** (evaluar candidatos), sobre la arquitectura de las entregas 1 a 6 (ver `docs/ARQUITECTURA.md`).

## Puesta en marcha

### 1. Base de datos
```bash
docker compose up -d
```

### 2. Backend (Python 3.11+)
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python -m app.seed
uvicorn app.main:app --reload
```

### 3. Frontend
```bash
cd frontend
npm install
npm run dev
```

## Credenciales de prueba (AUTH_MODE=mock)
- Consultor: usuario `CONSULTOR` / contraseña `consultor123`
- Candidato: tipo `DNI`, número `12345678`, clave `AB12CD34`

Para usar el LDAP real, poner `AUTH_MODE=ldap` y completar `LDAP_SERVER` y
`LDAP_USER_DN_TEMPLATE` en `backend/.env` (en producción `ldaps://servidor:636`).
El consultor debe existir también en la tabla `consultor` (legajo + username).

## Probar CU006 y CU025
- **CU006:** menú *Importar candidatos* → elegir `docs/ejemplo_candidatos.csv` (crea 2, actualiza 1 y da de baja 1).
- **CU025:** menú *Evaluar candidatos*. Con los datos de prueba:
  - `DESARROLLADOR BACKEND` / `MERCADOLIBRE` y `ANALISTA FUNCIONAL` / `ACCENTURE` se pueden evaluar.
  - `QA TESTER` / `GLOBANT` muestra el error de competencias no evaluables (su competencia tiene un solo factor con 1 pregunta).
  - El candidato `PEREZ JUAN` ya tiene un cuestionario activo, así que no puede evaluarse de nuevo.
  - Las claves generadas sirven para ingresar desde *Realizar cuestionario*.
