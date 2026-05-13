from config.db import Base, engine
from models import *

# Crear todas las tablas
Base.metadata.create_all(bind=engine)
print("✅ Tablas creadas exitosamente, incluyendo 'administrador'")
