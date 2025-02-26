from src.BaseDatos.Conexion import get_db
from src.BaseDatos.Tablas import Categoria
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

class Categorias:
    @staticmethod
    def generate_new_category_id(session):
        categorias = session.query(Categoria).all()
        max_id_num = 0
        for categoria in categorias:
            try:
                # Se asume que el ID tiene el formato CA-XXX
                numeric_part = int(categoria.idCat.split('-')[1])
                if numeric_part > max_id_num:
                    max_id_num = numeric_part
            except (IndexError, ValueError):
                continue
        new_number = max_id_num + 1
        new_id = f"CA-{new_number:03d}"
        return new_id

    @staticmethod
    def create_category(nombre, user_id):
        db = next(get_db())
        try:
            new_id = Categorias.generate_new_category_id(db)
            nueva_categoria = Categoria(
                idCat=new_id,
                nombre=nombre,
                fecha=datetime.utcnow(),
                user_id=user_id
            )
            db.add(nueva_categoria)
            db.commit()
            print(f"✔ Categoría creada con ID: {nueva_categoria.idCat}")
            return nueva_categoria
        except SQLAlchemyError as e:
            db.rollback()
            print("❌ Error al crear la categoría:", str(e))
            return None
        finally:
            db.close()

    @staticmethod
    def edit_category(idCat, new_nombre):
        db = next(get_db())
        try:
            categoria = db.query(Categoria).filter(Categoria.idCat == idCat).first()
            if not categoria:
                print(f"❌ No se encontró la categoría con ID: {idCat}")
                return None
            categoria.nombre = new_nombre
            db.commit()
            print(f"✔ Categoría {idCat} actualizada al nombre: {new_nombre}")
            return categoria
        except SQLAlchemyError as e:
            db.rollback()
            print("❌ Error al editar la categoría:", str(e))
            return None
        finally:
            db.close()

    @staticmethod
    def delete_category(idCat):
        db = next(get_db())
        try:
            categoria = db.query(Categoria).filter(Categoria.idCat == idCat).first()
            if not categoria:
                print(f"❌ No se encontró la categoría con ID: {idCat}")
                return False
            db.delete(categoria)
            db.commit()
            print(f"✔ Categoría con ID: {idCat} eliminada exitosamente.")
            return True
        except SQLAlchemyError as e:
            db.rollback()
            print("❌ Error al eliminar la categoría:", str(e))
            return False
        finally:
            db.close()

    @staticmethod
    def listar_categorias(user_id):
        db = next(get_db())
        try:
            categorias = db.query(Categoria).filter(Categoria.user_id == user_id).all()
            return categorias
        except SQLAlchemyError as e:
            print("❌ Error al listar las categorías:", str(e))
            return []
        finally:
            db.close()

