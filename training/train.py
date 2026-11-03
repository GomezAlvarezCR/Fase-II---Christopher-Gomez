"""Entrenamiento reproducible de un clasificador de intenciones (datos sintéticos)."""
import json
from datetime import datetime, timezone
from pathlib import Path

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.dummy import DummyClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "training" / "data.json"
MODEL = ROOT / "model" / "intent_model.joblib"
METRICS = ROOT / "model" / "metricas_evaluacion.json"


def main():
    data = json.loads(DATASET.read_text(encoding="utf-8"))["ejemplos"]
    examples = [(text, label) for label, texts in data.items() for text in texts]
    x, y = zip(*examples)
    x_train, x_test, y_train, y_test = train_test_split(
        list(x), list(y), test_size=0.25, random_state=42, stratify=list(y)
    )

    def pipeline():
        return Pipeline([
            ("tfidf", TfidfVectorizer(strip_accents="unicode", lowercase=True, analyzer="char_wb", ngram_range=(2, 5), sublinear_tf=True)),
            ("clf", LogisticRegression(max_iter=3000, C=6.0, random_state=42)),
        ])

    evaluation_model = pipeline()
    evaluation_model.fit(x_train, y_train)
    predictions = evaluation_model.predict(x_test)
    labels = sorted(data.keys())
    baseline = DummyClassifier(strategy="most_frequent")
    baseline.fit(x_train, y_train)
    baseline_pred = baseline.predict(x_test)
    metrics = {
        "nota": "Evaluación interna de datos sintéticos; NO demuestra eficacia clínica ni generalización a pacientes reales.",
        "algoritmo": "TF-IDF caracteres (2-5) + LogisticRegression",
        "baseline_mayoria_accuracy": round(float(accuracy_score(y_test, baseline_pred)),4),
        "baseline_mayoria_f1_macro": round(float(f1_score(y_test, baseline_pred, average="macro")),4),
        "random_state": 42,
        "ejemplos_totales": len(x),
        "ejemplos_entrenamiento": len(x_train),
        "ejemplos_prueba": len(x_test),
        "accuracy": round(float(accuracy_score(y_test, predictions)), 4),
        "f1_macro": round(float(f1_score(y_test, predictions, average="macro")), 4),
        "etiquetas": labels,
        "matriz_confusion": confusion_matrix(y_test, predictions, labels=labels).tolist(),
        "reporte_por_clase": classification_report(y_test, predictions, output_dict=True, zero_division=0),
    }
    final_model = pipeline()
    final_model.fit(x, y)
    metadata = {
        "nombre": "nakashima-intents-v1",
        "version": "1.0.0",
        "entrenado_utc": datetime.now(timezone.utc).isoformat(),
        "etiquetas": labels,
        "datos": "Sintéticos, generados para fines educativos",
        "modelo_supervisado": True,
        "no_es_llm": True,
    }
    MODEL.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"pipeline": final_model, "metadata": metadata}, MODEL)
    METRICS.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Modelo guardado:", MODEL)
    print(f"Evaluación (partición 75/25): accuracy={metrics['accuracy']:.3f}; F1 macro={metrics['f1_macro']:.3f}")
    print("Nota: métricas limitadas a textos sintéticos.")


if __name__ == "__main__":
    main()
