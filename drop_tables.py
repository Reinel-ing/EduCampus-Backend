from config.db import Base, engine

# ADVERTENCIA: Esto eliminará todas las tablas y los datos contenidos en ellas.
# Úsalo solo si estás seguro de que quieres borrar la base de datos de desarrollo.

if __name__ == "__main__":
    confirm = input("¿Estás seguro de que quieres eliminar todas las tablas y datos? (si/no): ")
    if confirm.lower() in ("si", "s", "yes", "y"):
        Base.metadata.drop_all(bind=engine)
        print("🗑️  Todas las tablas han sido eliminadas correctamente.")
    else:
        print("Operación cancelada. No se eliminaron tablas.")
