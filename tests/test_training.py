"""Integridad básica del artefacto ML y del archivo de evaluación."""
import json
from pathlib import Path
from app.predictor import load_artifact

ROOT=Path(__file__).resolve().parents[1]


def test_artefacto_entrenado():
    data=load_artifact()
    assert 'pipeline' in data and 'metadata' in data
    assert data['metadata']['no_es_llm'] is True
    assert len(data['metadata']['etiquetas']) == 7


def test_metricas_y_particion():
    metrics=json.loads((ROOT/'model/metricas_evaluacion.json').read_text(encoding='utf-8'))
    assert metrics['ejemplos_totales'] == metrics['ejemplos_entrenamiento']+metrics['ejemplos_prueba']
    assert 0 <= metrics['accuracy'] <= 1
    assert 0 <= metrics['f1_macro'] <= 1
