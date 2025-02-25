from src.BaseDatos.Conexion import get_db
from src.BaseDatos.Tablas import User
from sqlalchemy.exc import SQLAlchemyError
from passlib.hash import bcrypt

class Usuarios:
    @staticmethod
    def generate_new_user_id(session):
        users = session.query(User).all()
        max_id_num = 0
        for user in users:
            try:
                numeric_part = int(user.id.split('-')[1])
                if numeric_part > max_id_num:
                    max_id_num = numeric_part
            except (IndexError, ValueError):
                continue
        new_number = max_id_num + 1
        return f"NUS-{new_number:03d}"

    @staticmethod
    def encrypt_password(password: str) -> str:
        return bcrypt.hash(password)

    @staticmethod
    def create_user(name, email, password):
        try:
            db = next(get_db())
        except Exception as e:
            print("❌ Error al conectar con la base de datos:", str(e))
            return None

        try:
            new_id = Usuarios.generate_new_user_id(db)
            encrypted_password = Usuarios.encrypt_password(password)
            new_user = User(
                id=new_id,
                name=name,
                email=email,
                password=encrypted_password
            )
            db.add(new_user)
            db.commit()
            print(f"✔ Usuario creado con ID: {new_user.id}")
            return new_user
        except SQLAlchemyError as e:
            db.rollback()
            print("❌ Error al crear el usuario:", str(e))
            return None
        finally:
            db.close()

    @staticmethod
    def validate_user(email, password):
        try:
            db = next(get_db())
        except Exception as e:
            print("❌ Error al conectar con la base de datos:", str(e))
            return None

        try:
            user = db.query(User).filter(User.email == email).first()
            if user and bcrypt.verify(password, user.password):
                print(f"✔ Usuario autenticado con ID: {user.id}")
                return user
            else:
                print("❌ Credenciales inválidas")
                return None
        except SQLAlchemyError as e:
            db.rollback()
            print("❌ Error al validar el usuario:", str(e))
            return None
        finally:
            db.close()

if __name__ == "__main__":
    email_address = "julio@gmail.com"
    password = "123456"

    usuario_validado = Usuarios.validate_user(email_address, password)
    if usuario_validado:
        print("Inicio de sesión exitoso.")
    else:
        print("Inicio de sesión fallido.")
        