"""Smoke test: ejecuta peticiones internas sin iniciar un servidor externo."""
from fastapi.testclient import TestClient
from app.main import app

with TestClient(app) as client:
    for path in ['/', '/health']:
        response=client.get(path)
        print(f'GET {path}: HTTP {response.status_code}')
        assert response.status_code == 200
    for question in ['¿Qué horarios tienen?', 'Quiero agendar una cita', 'Tengo dolor de muela']:
        response=client.post('/api/consultar',json={'mensaje':question})
        response.raise_for_status()
        answer=response.json()
        print(f'POST /api/consultar | {question} => {answer["categoria"]} ({answer["metodo"]})')
print('Smoke tests completados correctamente.')
