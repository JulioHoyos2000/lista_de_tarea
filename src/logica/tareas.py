from src.BaseDatos.Conexion import get_db
from src.BaseDatos.Tablas import Tarea, Categoria
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

class Tareas:
    @staticmethod
    def generate_new_task_id(session):
        tareas = session.query(Tarea).all()
        max_id_num = 0
        for tarea in tareas:
            try:
                # Se asume que el ID tiene el formato TR-XXX
                numeric_part = int(tarea.idTarea.split('-')[1])
                if numeric_part > max_id_num:
                    max_id_num = numeric_part
            except (IndexError, ValueError):
                continue
        new_number = max_id_num + 1
        new_id = f"TR-{new_number:03d}"
        return new_id

    @staticmethod
    def crear_tarea(id_usuario, titulo, id_categoria, prioridad, estado, fecha):
        db = next(get_db())
        try:
            new_id = Tareas.generate_new_task_id(db)
            # Convertir fecha a objeto datetime si es un string
            if isinstance(fecha, str):
                fecha_dt = datetime.strptime(fecha, "%Y-%m-%d")
            else:
                fecha_dt = fecha
            nueva_tarea = Tarea(
                idTarea=new_id,
                id_usuario=id_usuario,
                titulo=titulo,
                id_categoria=id_categoria,
                prioridad=prioridad,
                estado=estado,
                fecha=fecha_dt
            )
            db.add(nueva_tarea)
            db.commit()
            print(f"✔ Tarea creada con ID: {nueva_tarea.idTarea}")
            return nueva_tarea
        except SQLAlchemyError as e:
            db.rollback()
            print("❌ Error al crear la tarea:", str(e))
            return None
        finally:
            db.close()

    @staticmethod
    def editar_tarea(id_tarea, titulo=None, id_categoria=None, prioridad=None, estado=None, fecha=None):
        db = next(get_db())
        try:
            tarea = db.query(Tarea).filter(Tarea.idTarea == id_tarea).first()
            if not tarea:
                print(f"❌ No se encontró la tarea con ID: {id_tarea}")
                return None
            if titulo is not None:
                tarea.titulo = titulo
            if id_categoria is not None:
                tarea.id_categoria = id_categoria
            if prioridad is not None:
                tarea.prioridad = prioridad
            if estado is not None:
                tarea.estado = estado
            if fecha is not None:
                if isinstance(fecha, str):
                    tarea.fecha = datetime.strptime(fecha, "%Y-%m-%d")
                else:
                    tarea.fecha = fecha
            db.commit()
            print(f"✔ Tarea {id_tarea} actualizada exitosamente.")
            return tarea
        except SQLAlchemyError as e:
            db.rollback()
            print("❌ Error al editar la tarea:", str(e))
            return None
        finally:
            db.close()

    @staticmethod
    def eliminar_tarea(id_tarea):

        db = next(get_db())
        try:
            tarea = db.query(Tarea).filter(Tarea.idTarea == id_tarea).first()
            if not tarea:
                print(f"❌ No se encontró la tarea con ID: {id_tarea}")
                return False
            db.delete(tarea)
            db.commit()
            print(f"✔ Tarea con ID: {id_tarea} eliminada exitosamente.")
            return True
        except SQLAlchemyError as e:
            db.rollback()
            print("❌ Error al eliminar la tarea:", str(e))
            return False
        finally:
            db.close()

    @staticmethod
    def listar_tareas():
        db = next(get_db())
        try:
            resultados = (
                db.query(Tarea, Categoria)
                .outerjoin(Categoria, Tarea.id_categoria == Categoria.idCat)
                .all()
            )
            tareas = []
            for tarea, categoria in resultados:
                tareas.append({
                    "idTarea": tarea.idTarea,
                    "id_usuario": tarea.id_usuario,
                    "titulo": tarea.titulo,
                    "categoria": categoria.nombre if categoria is not None else None,
                    "prioridad": tarea.prioridad,
                    "estado": tarea.estado,
                    "fecha": tarea.fecha
                })
            return tareas
        except SQLAlchemyError as e:
            print("❌ Error al listar las tareas:", str(e))
            return []
        finally:
            db.close()

    @staticmethod
    def filtrar_por_prioridad(prioridad):
        db = next(get_db())
        try:
            tareas = db.query(Tarea).filter(Tarea.prioridad == prioridad).all()
            return tareas
        except SQLAlchemyError as e:
            print("❌ Error al filtrar tareas por prioridad:", str(e))
            return []
        finally:
            db.close()

    @staticmethod
    def filtrar_por_estado(estado):
        db = next(get_db())
        try:
            tareas = db.query(Tarea).filter(Tarea.estado == estado).all()
            return tareas
        except SQLAlchemyError as e:
            print("❌ Error al filtrar tareas por estado:", str(e))
            return []
        finally:
            db.close()

    @staticmethod
    def filtrar_por_categoria(nombre_categoria):
        db = next(get_db())
        try:
            tareas = (
                db.query(Tarea)
                .join(Tarea.categoria_obj)
                .filter(Categoria.nombre == nombre_categoria)
                .all()
            )
            return tareas
        except SQLAlchemyError as e:
            print("❌ Error al filtrar tareas por categoría:", str(e))
            return []
        finally:
            db.close()

    @staticmethod
    def buscar_por_titulo(titulo):
        db = next(get_db())
        try:
            tareas = (
                db.query(Tarea, Categoria)
                .outerjoin(Categoria, Tarea.id_categoria == Categoria.idCat)
                .filter(Tarea.titulo.ilike(f"%{titulo}%"))
                .all()
            )

            resultado = []
            for tarea, categoria in tareas:
                resultado.append({
                    "idTarea": tarea.idTarea,
                    "id_usuario": tarea.id_usuario,
                    "titulo": tarea.titulo,
                    "categoria": categoria.nombre if categoria is not None else None,
                    "prioridad": tarea.prioridad,
                    "estado": tarea.estado,
                    "fecha": tarea.fecha
                })
            return resultado
        except SQLAlchemyError as e:
            print("❌ Error al buscar tareas por título:", str(e))
            return []
        finally:
            db.close()
            