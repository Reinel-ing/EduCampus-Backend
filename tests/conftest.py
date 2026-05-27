"""
conftest.py
Configuración compartida para pruebas de integración.
Usa SQLite en memoria para no afectar la base de datos real.
"""
import os
import sys
from unittest.mock import MagicMock

# ─── 1. URL de base de datos de prueba ANTES de cualquier import ──────────
os.environ["DATABASE_URL"] = "sqlite:///./test_integration.db"

# ─── 2. Reemplazar servicios externos (email, notificaciones) ─────────────
# Se hace antes de que los routers los importen
sys.modules["service.email_service"]       = MagicMock()
sys.modules["service.notificacion_service"] = MagicMock()

# ─── 3. JSONB → JSON (SQLite no tiene JSONB) ──────────────────────────────
from sqlalchemy import JSON as _JSON
import sqlalchemy.dialects.postgresql as _pgd
_pgd.JSONB = _JSON

# ─── 4. Importar app e infraestructura ───────────────────────────────────
import pytest
from fastapi.testclient import TestClient
from config.db import Base, engine
import models  # registra todos los modelos en Base.metadata

# ─── 5. Crear tablas en SQLite (limpia y recrea en cada ejecución) ───────
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

# ─── 6. Importar app con todos los routers ────────────────────────────────
from main import app


@pytest.fixture(scope="session")
def client():
    """Cliente de prueba — comparte estado durante toda la sesión."""
    with TestClient(app) as c:
        yield c
