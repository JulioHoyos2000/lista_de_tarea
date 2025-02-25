import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Configuración de logging
logging.basicConfig(level=logging.INFO)


DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    logging.warning("⚠️ No se encontró DATABASE_URL, usando la configuración por defecto (SQLite).")
    DATABASE_URL = "sqlite:///C:/Users/USUARIO/IdeaProjects/lista_de_tarea/src/BaseDatos/db.sqlite3"


try:
    connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

    engine = create_engine(DATABASE_URL, connect_args=connect_args)
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base = declarative_base()

    logging.info("✅ Conexión exitosa a la base de datos.")

except Exception as e:
    logging.error(f"❌ Error de conexión a la base de datos: {str(e)}", exc_info=True)
    raise SystemExit("No se pudo conectar a la base de datos.")

def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        logging.error(f"⚠️ Error en la sesión de base de datos: {str(e)}", exc_info=True)
        raise
    finally:
        db.close()
