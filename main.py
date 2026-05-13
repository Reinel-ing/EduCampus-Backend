from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
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
from routers.auth import router as auth_router
from routers.administrador import router as administrador_router

app = FastAPI(
    title="API Vortal Académico",
    description="""
<h2 style='color:#2e86de;'>Bienvenido al sistema académico Vortal</h2>
<p>Esta API gestiona docentes, estudiantes, cursos, inscripciones, calificaciones, asistencia, material didáctico y configuración institucional.<br>
Utiliza <b>FastAPI</b>, <b>SQLAlchemy</b>, <b>Pydantic v2</b>, <b>Alembic</b> y <b>PostgreSQL Neon</b>.<br>
<br>
<b>¡Explora los endpoints y prueba el sistema!</b></p>
<ul>
  <li>CRUD completo para todas las entidades</li>
  <li>Validaciones automáticas y respuestas detalladas</li>
  <li>Dashboard con estadísticas académicas</li>
</ul>
""",
    version="1.0.0",
    contact={
        "name": "Vortal API Team",
        "email": "contacto@institucion.edu"
    },
    docs_url=None, # Desactivamos la docs por defecto
    redoc_url=None
)

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title="Documentación Interactiva Vortal",
        swagger_favicon_url="https://fastapi.tiangolo.com/img/favicon.png",
        swagger_ui_parameters={
            "defaultModelsExpandDepth": -1,
            "docExpansion": "none",
            "displayRequestDuration": True,
            "filter": True,
        },
        oauth2_redirect_url=None
    )

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def root():
    return """
    <div style='font-family:Segoe UI,Arial,sans-serif;max-width:700px;margin:auto;padding:2em;'>
      <img src='https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png' alt='FastAPI' style='height:60px;float:right;'>
      <h1 style='color:#2e86de;'>API Vortal Académico</h1>
      <p>Bienvenido al sistema académico Vortal.<br>
      Accede a la <a href='/docs' style='color:#27ae60;font-weight:bold;'>documentación interactiva</a> para probar todos los endpoints.</p>
      <ul>
        <li>Gestión de docentes, estudiantes y cursos</li>
        <li>Inscripciones, calificaciones y asistencia</li>
        <li>Material didáctico y configuración institucional</li>
        <li>Dashboard de estadísticas</li>
      </ul>
      <hr>
      <p style='color:#888;'>Powered by FastAPI, SQLAlchemy, Pydantic v2, Alembic y Neon PostgreSQL</p>
    </div>
    """

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
