from src.BaseDatos.Conexion import engine, Base
from src.BaseDatos.Tablas import User, Categoria, Tarea, Notification, Notas

def create_database():
    Base.metadata.create_all(bind=engine)
    print("✔ Base de datos y tablas creadas con éxito.")

if __name__ == "__main__":
    create_database()