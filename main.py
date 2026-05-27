"""
main.py
Punto de entrada de la API EduCampus.

Configura la aplicación FastAPI, el middleware CORS y registra
todos los routers del sistema académico.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse

from routers.auth import router as auth_router
from routers.administrador import router as administrador_router
from routers.docentes import router as docentes_router
from routers.estudiantes import router as estudiantes_router
from routers.cursos import router as cursos_router
from routers.inscripciones import router as inscripciones_router
from routers.calificaciones import router as calificaciones_router
from routers.asistencia import router as asistencia_router
from routers.material import router as material_router
from routers.configuracion import router as configuracion_router
from routers.dashboard import router as dashboard_router
from routers.reportes import router as reportes_router
from routers.notificaciones import router as notificaciones_router
from routers.actividades import router as actividades_router


app = FastAPI(
    title="API EduCampus",
    description="Sistema de gestión académica para docentes, estudiantes y administradores.",
    version="1.0.0",
    docs_url=None,
    redoc_url=None,
)


# Documentación interactiva personalizada
@app.get("/docs", include_in_schema=False)
async def swagger_ui():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title="EduCampus – Documentación API",
        swagger_favicon_url="https://fastapi.tiangolo.com/img/favicon.png",
        swagger_ui_parameters={
            "defaultModelsExpandDepth": -1,
            "docExpansion": "none",
            "displayRequestDuration": True,
            "filter": True,
        },
        oauth2_redirect_url=None,
    )


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def root():
    """Página de bienvenida con enlace a la documentación."""
    return """
    <html><body style="font-family:Segoe UI,sans-serif;max-width:680px;margin:3em auto;color:#1e293b">
      <h1 style="color:#1e40af">API EduCampus</h1>
      <p>Sistema académico en línea. Accede a la
        <a href="/docs" style="color:#15803d;font-weight:600">documentación interactiva</a>
        para explorar los endpoints disponibles.</p>
      <hr style="border:none;border-top:1px solid #e2e8f0;margin:1.5em 0">
      <p style="color:#94a3b8;font-size:13px">FastAPI · SQLAlchemy · Pydantic v2 · PostgreSQL (Neon)</p>
    </body></html>
    """


# Permite solicitudes desde el frontend React en cualquier origen (desarrollo y producción)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registro de routers por dominio funcional
app.include_router(auth_router)
app.include_router(administrador_router)
app.include_router(docentes_router)
app.include_router(estudiantes_router)
app.include_router(cursos_router)
app.include_router(inscripciones_router)
app.include_router(calificaciones_router)
app.include_router(asistencia_router)
app.include_router(material_router)
app.include_router(configuracion_router)
app.include_router(dashboard_router)
app.include_router(reportes_router)
app.include_router(notificaciones_router)
app.include_router(actividades_router)
