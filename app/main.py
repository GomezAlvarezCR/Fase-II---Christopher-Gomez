"""API REST y frontend del prototipo académico Fase II."""
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, field_validator

from app.predictor import load_artifact, predict_intent

ROOT = Path(__file__).resolve().parents[1]


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_artifact()
    yield


app = FastAPI(title="Nakashima IA - Prototipo administrativo", version="1.0.0", lifespan=lifespan)


class ConsultaEntrada(BaseModel):
    mensaje: str = Field(min_length=1, max_length=500, description="Consulta administrativa; no incluir datos sensibles")

    @field_validator("mensaje")
    @classmethod
    def nonempty(cls, v):
        if not v.strip():
            raise ValueError("El mensaje no puede contener solo espacios")
        return v


class ConsultaSalida(BaseModel):
    categoria: str
    respuesta: str
    confianza: float | None
    requiere_humano: bool
    metodo: str


@app.get("/")
def frontend():
    return FileResponse(ROOT / "app" / "static" / "index.html")


@app.get("/health")
def health():
    model = load_artifact()
    return {"estado": "ok", "modelo_cargado": True, "version_modelo": model["metadata"]["version"]}


@app.post("/api/consultar", response_model=ConsultaSalida)
def consultar(payload: ConsultaEntrada):
    # No persiste mensajes, IPs, datos personales ni historias clínicas.
    return predict_intent(payload.mensaje)
