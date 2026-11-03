# Guía práctica de entrega — Fase II

## Checklist de la rúbrica

| Criterio | Qué demostrar | Evidencia sugerida |
|---|---|---|
| 1. Docker (25 pt) | `Dockerfile`, `docker build`, contenedor iniciado y endpoint operativo | Captura 01 + 02 |
| 2. API/frontend/backend (25 pt) | Flujo desde el navegador hasta POST `/api/consultar` y respuesta JSON | Captura 03 + 04 |
| 3. Pruebas (25 pt) | pytest, casos extremos, reflexión y métricas con matriz de confusión | Captura 05 + figuras |
| 4. Repositorio/documentación (25 pt) | GitHub ordenado, README con instrucciones replicables | Captura 06 + URL |

## Capturas que debes obtener en tu computadora

1. **`evidencias/01_docker_build.png`**: terminal con el resultado final exitoso de `docker build -t nakashima-fase2:1.0 .`.
2. **`evidencias/02_docker_run.png`**: terminal con `docker ps` y navegador en `http://localhost:8000/health` mostrando `modelo_cargado: true`.
3. **`evidencias/03_frontend.png`**: navegador `http://localhost:8000` mostrando una consulta de horarios/citas y su respuesta.
4. **`evidencias/04_api_seguridad.png`**: Swagger `http://localhost:8000/docs` probando `Tengo dolor de muela` y mostrando `requiere_humano: true`. Otra opción es captura del frontend con esta consulta.
5. **`evidencias/05_pruebas.png`**: terminal con `python -m pytest -v` y resultado completo sin errores.
6. **`evidencias/06_github.png`**: página principal del repositorio (estructura y README visibles).

**Nota:** Las figuras generadas automáticamente en `figuras/` son resultados de evaluación, no sustituyen las capturas reales de Docker.

## Cómo crear el repositorio

1. Crear un repositorio público o privado según la instrucción del profesor, por ejemplo `Proyecto-Fase-II-Nakashima-IA`.
2. Subir los archivos **de la carpeta raíz** de este proyecto (no añadir la carpeta `.venv`).
3. Comprobar que el README se ve en GitHub y que `Dockerfile`, `app/`, `model/`, `training/`, `tests/` y `figuras/` están presentes.
4. Subir a `evidencias/` las capturas reales, preferentemente después de confirmar los comandos localmente.
5. Entregar la URL del repositorio y, **solo si el campus solicita documento**, el reporte en PDF con las capturas.

## Importante

No hay instrucciones específicas de entrega en estos tres archivos aparte de la rúbrica. Si la plataforma de la actividad pide archivos adicionales o un enlace determinado, seguir esa consigna; no asumir que solo el ZIP es suficiente.

## Estado de validación

- [x] Modelo entrenado y guardado.
- [x] API probada con TestClient.
- [x] Interfaz servida en ruta `/`.
- [x] Pruebas automatizadas realizadas en Python.
- [x] Dockerfile redactado.
- [ ] Construcción y ejecución Docker reales en tu equipo (pendiente).
- [ ] Capturas de ejecución Docker y GitHub (pendientes).
- [ ] URL de GitHub y revisión final (pendientes).
