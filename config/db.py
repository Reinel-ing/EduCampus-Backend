from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv
import logging

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    future=True
)

try:
    # Probar la conexión
    with engine.connect() as connection:
        logging.basicConfig(level=logging.INFO)
        logging.info("Conexión a la base de datos exitosa.")
except Exception as e:
    logging.basicConfig(level=logging.ERROR)
    logging.error(f"Error al conectar a la base de datos: {e}")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
