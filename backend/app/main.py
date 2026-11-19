from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .entidades import models  # noqa: F401  (registra las tablas)
from .infraestructura.database import Base, engine
from .interfaz import auth, candidatos


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(engine)  # en desarrollo; luego migrar a Alembic
    yield


app = FastAPI(title="Capit@l Humano – Evaluaciones", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(candidatos.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
