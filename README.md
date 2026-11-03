# Proyecto Fase II — Asistente administrativo de Clínica Nakashima

**Curso:** Gestión de proyectos de inteligencia artificial — Universidad Tecmilenio  
**Tipo:** Prototipo académico local, con datos sintéticos  
**Alcance:** Clasificación supervisada de consultas administrativas, respuestas preaprobadas y derivación a personal humano. **No diagnostica ni prescribe.**

## 1. Relación con Fase I

La Fase I propuso un asistente de información inicial y solicitudes de cita para Clínica Nakashima. Esta Fase II implementa una versión reducida y verificable de ese flujo para demostrar integración frontend/backend, modelo ML, API REST, pruebas y contenerización. No implementa una agenda real, un LLM ni un sistema clínico de producción.

## 2. Arquitectura

```text
Usuario (navegador web)
        │ HTML / CSS / JS
        ▼
Frontend (app/static/index.html)
        │ POST JSON /api/consultar
        ▼
Backend FastAPI (app/main.py)
        │
        ├─ Validación de entrada (Pydantic: 1–500 caracteres)
        │
        └─ Clasificación / seguridad (app/predictor.py)
                 ├─ Reglas de seguridad para consultas clínicas → humano
                 ├─ TF-IDF caracteres + Regresión logística → intención
                 └─ Umbral de confianza → respuesta o derivación
                          │
                          ▼
                   Respuestas fijas administrativas
        │
        ▼
JSON de respuesta → Interfaz web
```

El modelo fue entrenado **offline** con 154 consultas creadas para el ejercicio, divididas en 7 categorías. Se evalúa con un conjunto estratificado de 25 % no usado durante el ajuste de evaluación. El artefacto final de inferencia se reentrena con los 154 ejemplos y se guarda en `model/intent_model.joblib` para arrancar sin entrenamiento durante el despliegue.

## 3. Estructura de archivos

```text
fase2_nakashima/
├── app/
│   ├── main.py                 # API, rutas web y validación
│   ├── predictor.py            # Predicción y reglas de seguridad
│   ├── knowledge.py            # Respuestas administrativas
│   └── static/index.html       # Frontend interactivo
├── training/
│   ├── data.json               # 154 mensajes SINTÉTICOS
│   └── train.py                # Entrenamiento reproducible
├── model/
│   ├── intent_model.joblib     # Artefacto ML entrenado
│   └── metricas_evaluacion.json
├── tests/
│   ├── test_api.py             # Pruebas HTTP, integración y extremos
│   └── test_training.py       # Pruebas del artefacto y métricas
├── scripts/
│   ├── verificar.py            # Pruebas rápidas sin servidor externo
│   └── graficas.py             # Genera figuras para el reporte
├── figuras/                    # Gráficos de evaluación
├── evidencias/                 # Agregar capturas tomadas en la PC
├── Dockerfile
├── .dockerignore
├── requirements.txt
├── requirements-dev.txt
├── REPORTE_BORRADOR.md
└── GUIA_ENTREGA.md
```

## 4. Requisitos

- Python 3.11.
- Para el **despliegue local Docker**: Docker Desktop instalado y activo (Windows, Mac o Linux).
- Para probar el modelo sin Docker: Python 3.11 y las dependencias de `requirements-dev.txt`.
- No requiere GPU, API de pago, credenciales, conexión a base de datos ni datos de pacientes.

## 5. Ejecución local sin Docker (Windows PowerShell)

Abrir una terminal dentro de la carpeta `fase2_nakashima`:

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python -m pytest -v
python -m scripts.verificar
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Visitar **http://localhost:8000** en el navegador. Documentación interactiva de API: **http://localhost:8000/docs**. Estado del sistema: **http://localhost:8000/health**.

Si Windows bloquea `Activate.ps1`, se puede invocar `.venv\Scripts\python.exe` en lugar de activar el entorno.

Para repetir el entrenamiento con la misma partición aleatoria:

```powershell
python training/train.py
```

El script regenera el modelo, la métrica y el artefacto final. Para reproducir los resultados, mantener el dataset y las versiones de las dependencias sin cambios.

## 6. Contenerización con Docker (Windows PowerShell)

Desde la **carpeta raíz del proyecto**:

```powershell
docker --version
docker build -t nakashima-fase2:1.0 .
docker run --rm -d --name nakashima-ia -p 8000:8000 nakashima-fase2:1.0
docker ps
```

Comprobar en el navegador:

- `http://localhost:8000` — interfaz web.
- `http://localhost:8000/health` — estado y versión.
- `http://localhost:8000/docs` — documentación Swagger.

Probar API desde otra terminal PowerShell:

```powershell
Invoke-RestMethod -Uri http://localhost:8000/api/consultar -Method Post -ContentType "application/json" -Body '{"mensaje":"Quiero agendar una cita"}'
```

Para consultar los últimos registros y detener:

```powershell
docker logs nakashima-ia
docker stop nakashima-ia
```

El contenedor usa usuario no root, puerto 8000, healthcheck HTTP y no almacena historiales de consultas. **El paquete incluye Dockerfile, pero la ejecución dentro de Docker requiere validación en la computadora con Docker Desktop**.

## 7. API REST

### GET `/health`

Respuesta de ejemplo:

```json
{"estado":"ok","modelo_cargado":true,"version_modelo":"1.0.0"}
```

### POST `/api/consultar`

Solicitud:

```json
{"mensaje":"¿A qué hora abren?"}
```

Respuesta ilustrativa (el valor de confianza depende del artefacto):

```json
{
  "categoria":"horarios",
  "respuesta":"Nuestro horario habitual es de lunes a sábado, de 9:00 a 18:00. Confirma con recepción antes de acudir, pues puede variar por sucursal o fecha.",
  "confianza":0.8,
  "requiere_humano":false,
  "metodo":"clasificador_ml"
}
```

Las preguntas clínicas detectadas mediante reglas generan `categoria: consulta_clinica`, `metodo: regla_seguridad` y `requiere_humano: true`, sin indicaciones clínicas. Los mensajes vacíos o de más de 500 caracteres regresan HTTP 422.

## 8. Pruebas y evaluación

```powershell
python -m pytest -v
python -m scripts.verificar
python -m scripts.graficas
```

Las pruebas revisan carga del modelo, disponibilidad de frontend, comunicación API, clasificación de preguntas administrativas, derivación de consultas clínicas, casos mixtos, mensajes vacíos, entradas largas, caracteres especiales, posible inyección HTML y preguntas fuera del dominio.

La evaluación en `metricas_evaluacion.json` usa **39 ejemplos sintéticos reservados** en la partición 75/25. El objetivo no es demostrar desempeño en producción: los ejemplos son pequeños, redactados artificialmente y susceptibles a sesgo de formulación. Se requiere evaluación con datos autorizados, anonimización y revisión experta antes de cualquier despliegue real.

## 9. Seguridad, límites y gobernanza

- **No LLM:** El componente de IA es un clasificador supervisado TF-IDF + regresión logística; las respuestas se seleccionan de contenido fijo, no se generan libremente.
- **No información clínica personalizada:** consultas con términos sensibles se derivan a una persona; no interpreta fotografías ni diagnósticos.
- **No agenda real:** la solicitud de cita se transfiere a recepción, que confirma disponibilidad.
- **Privacidad:** no existe base de datos, almacenamiento de mensajes ni archivos de pacientes; se recomienda no ingresar datos personales.
- **Control de conocimiento:** actualizar horarios, servicios y precios desde fuentes aprobadas, con revisión humana.
- **Riesgos residuales:** frases clínicas sin palabras clave, errores de clasificación, incertidumbre no calibrada, cambios de vocabulario y falta de evaluación con usuarios reales.
- **Gobernanza:** documentar versión del dataset, modelo, artefacto, pruebas, propietario y procedimiento de actualización antes de producción.
- **Seguridad de artefactos:** `joblib` deserializa objetos de Python; únicamente cargar el archivo entrenado y controlado por el proyecto.

## 10. Evidencias y entrega

Consultar `GUIA_ENTREGA.md` para obtener las seis capturas sugeridas (build, contenedor en ejecución, frontend, API, pytest y repositorio). No afirmar que Docker fue validado hasta ejecutarlo exitosamente en tu equipo.

## 11. Material de apoyo del curso

- Tecmilenio. Tema 15. *Despliegue local* (material proporcionado en clase).
- Tecmilenio. Tema 16. *Despliegue en la nube* (material proporcionado en clase).
- Tecmilenio. *Rúbrica de evaluación para proyecto fase 2* (material proporcionado en clase).
- ISO/IEC 23053:2022, marco de referencia de sistemas de IA con ML, mencionado en el Tema 16. La estructura de documentación se inspira en su enfoque, **sin declarar certificación o conformidad formal**.

## 12. Documento editable

`docs/Reporte_Editable.docx` contiene un informe con arquitectura, resultados, figuras y limitaciones. `docs/Reporte_PDF_Borrador.pdf` es una versión para lectura. **Ambos son borradores** hasta agregar la URL del repositorio y las capturas de la ejecución real en Docker. Estas evidencias no se deben inventar.
