"""Clasificación supervisada + controles explícitos para consultas clínicas."""
import re
from functools import lru_cache
from pathlib import Path
import joblib

from app.knowledge import RESPUESTAS

MODEL_FILE = Path(__file__).resolve().parents[1] / "model" / "intent_model.joblib"
UMBRAL_CONFIANZA = 0.42  # umbral operativo exploratorio, no calibrado clínicamente
CLINICAL_TERMS = re.compile(
    r"\b(?:dolor|duele|sangr(?:a|ado|an)|fiebre|pus|infecci[oó]n|inflamad[oa]s?|" 
    r"antibi[oó]tico|medicamento|medicina|dosis|diagn[oó]stico|radiograf[ií]a|"
    r"caries|muela rota|fractur[ao]|urgencia|ibuprofeno|paracetamol|recetar|"
    r"hinchaz[oó]n|traumatismo|golpe[ée]?|hemorragia|receta)\b",
    re.IGNORECASE,
)


@lru_cache(maxsize=1)
def load_artifact():
    if not MODEL_FILE.is_file():
        raise FileNotFoundError("Falta model/intent_model.joblib; ejecutar python training/train.py")
    return joblib.load(MODEL_FILE)  # cargar únicamente el artefacto local y confiable del repositorio


def predict_intent(message: str):
    clean = " ".join(message.split())
    if CLINICAL_TERMS.search(clean):
        return {"categoria": "consulta_clinica", "respuesta": RESPUESTAS["consulta_clinica"],
                "confianza": None, "requiere_humano": True, "metodo": "regla_seguridad"}

    pipeline = load_artifact()["pipeline"]
    probs = pipeline.predict_proba([clean])[0]
    index = int(probs.argmax())
    confidence = float(probs[index])
    intent = str(pipeline.classes_[index])
    if confidence < UMBRAL_CONFIANZA:
        intent = "desconocida"

    return {"categoria": intent, "respuesta": RESPUESTAS[intent],
            "confianza": round(confidence, 4),
            "requiere_humano": intent in {"consulta_clinica", "desconocida", "cita", "costos"},
            "metodo": "clasificador_ml"}
