"""Pruebas automatizadas de integración, límites y mecanismos de seguridad."""
import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_health(client):
    r=client.get('/health')
    assert r.status_code == 200
    assert r.json()['modelo_cargado'] is True
    assert r.json()['estado'] == 'ok'


def test_frontend_visible(client):
    r=client.get('/')
    assert r.status_code == 200
    assert 'Clínica' in r.text
    assert "fetch('/api/consultar'" in r.text


@pytest.mark.parametrize('mensaje,categoria',[
    ('¿A qué hora abren?', 'horarios'),
    ('¿Dónde queda el consultorio?', 'ubicacion'),
    ('¿Qué tratamientos ofrecen?', 'servicios'),
    ('¿Cuánto cuesta la valoración?', 'costos'),
    ('Quiero agendar una cita', 'cita'),
])
def test_intenciones_administrativas(client,mensaje,categoria):
    r=client.post('/api/consultar',json={'mensaje':mensaje})
    assert r.status_code == 200
    data=r.json()
    assert data['categoria'] == categoria
    assert isinstance(data['respuesta'],str) and data['respuesta']
    assert data['metodo'] == 'clasificador_ml'


def test_consulta_clinica_derivada(client):
    r=client.post('/api/consultar',json={'mensaje':'Tengo fiebre y un dolor fuerte de muela, qué medicamento tomo'})
    assert r.status_code == 200
    data=r.json()
    assert data['categoria'] == 'consulta_clinica'
    assert data['requiere_humano'] is True
    assert data['metodo'] == 'regla_seguridad'
    assert 'No puedo diagnosticar' in data['respuesta']


def test_cita_con_dolor_prioriza_seguridad(client):
    r=client.post('/api/consultar',json={'mensaje':'Quiero una cita porque me duele mucho la muela'})
    assert r.json()['categoria']=='consulta_clinica'


@pytest.mark.parametrize('payload',[
    {}, {'mensaje':''}, {'mensaje':'  '}, {'mensaje':'x'*501},
])
def test_errores_entrada(client,payload):
    r=client.post('/api/consultar',json=payload)
    assert r.status_code == 422


def test_no_repite_entrada_clinica(client):
    text='tengo dolor de muela y mi telefono es 5555555555'
    result=client.post('/api/consultar',json={'mensaje':text}).json()
    assert '5555555555' not in result['respuesta']


def test_payload_html_no_reflejado(client):
    result=client.post('/api/consultar',json={'mensaje':'<script>alert(1)</script>'})
    assert result.status_code == 200
    assert '<script>' not in result.json()['respuesta']


def test_out_of_domain_muestra_rechazo_o_clasificacion(client):
    result=client.post('/api/consultar',json={'mensaje':'Quiero aprender a manejar un tractor en Marte'})
    assert result.status_code == 200
    assert result.json()['categoria'] == 'desconocida'
    assert result.json()['requiere_humano'] is True


def test_limite_500_caracteres_permitido(client):
    r=client.post('/api/consultar',json={'mensaje':'x'*500})
    assert r.status_code == 200
    assert r.json()['categoria'] == 'desconocida'


def test_emojis_sin_error(client):
    r=client.post('/api/consultar',json={'mensaje':'😄😄😄'})
    assert r.status_code == 200
    assert r.json()['categoria'] == 'desconocida'
