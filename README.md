# TP 2026 – Evaluación de candidatos (Capit@l Humano)

Etapa actual: **CU001 – Autenticar usuario**, sobre la arquitectura de las entregas 1 a 6 (ver `docs/ARQUITECTURA.md`).

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
uvicorn app.main:app --reload    # http://localhost:8000/docs
```

### 3. Frontend
```bash
cd frontend
npm install
npm run dev                      # http://localhost:5173
```

## Credenciales de prueba (AUTH_MODE=mock)
- Consultor: usuario `CONSULTOR` / contraseña `consultor123`
- Candidato: tipo `DNI`, número `12345678`, clave `AB12CD34`

Para usar el LDAP real, poner `AUTH_MODE=ldap` y completar `LDAP_SERVER` y
`LDAP_USER_DN_TEMPLATE` en `backend/.env` (en producción `ldaps://servidor:636`).
El consultor debe existir también en la tabla `consultor` (legajo + username).
