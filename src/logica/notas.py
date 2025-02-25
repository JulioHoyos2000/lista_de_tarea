import random
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from src.BaseDatos.Conexion import get_db
from src.BaseDatos.Tablas import Notas, Tarea

class NotasT:
    @staticmethod
    def generate_new_note_id(task_title: str):
        prefix = ''.join(filter(str.isalnum, task_title.upper()))[:4]
        if not prefix:
            prefix = "NTNT"
        random_number = random.randint(0, 9999)
        return f"{prefix}-{random_number:04d}"

    @staticmethod
    def create_note(task_title: str, content: str, created_at: datetime):
        db = next(get_db())
        try:
            tarea = db.query(Tarea).filter(Tarea.titulo == task_title).first()
            if not tarea:
                print("❌ Error: No se encontró una tarea con ese título.")
                return None

            task_id = tarea.idTarea
            new_id = NotasT.generate_new_note_id(task_title)

            new_note = Notas(
                idNota=new_id,
                task_id=task_id,
                content=content,
                created_at=created_at
            )

            db.add(new_note)
            db.commit()
            print(f"✔ Nota creada con ID: {new_note.idNota}")
            return new_note

        except SQLAlchemyError as e:
            db.rollback()
            print("❌ Error al crear la nota:", str(e))
            return None

        finally:
            db.close()

    @staticmethod
    def get_note_by_id(note_id: str):
        db = next(get_db())
        try:
            note = db.query(Notas).filter(Notas.idNota == note_id).first()
            if note:
                print(f"✔ Nota recuperada: ID: {note.idNota}, Contenido: {note.content}")
            else:
                print("❌ No se encontró la nota con ese ID.")
            return note
        except SQLAlchemyError as e:
            print("❌ Error al recuperar la nota:", str(e))
            return None
        finally:
            db.close()

    @staticmethod
    def get_note_by_task(task_title: str):
        db = next(get_db())
        try:
            tarea = db.query(Tarea).filter(Tarea.titulo == task_title).first()
            if not tarea:
                print("❌ No se encontró tarea con ese título")
                return None
            note = db.query(Notas).filter(Notas.task_id == tarea.idTarea).first()
            return note
        except SQLAlchemyError as e:
            print("❌ Error al recuperar nota por tarea:", str(e))
            return None
        finally:
            db.close()

    @staticmethod
    def update_note(note_id: str, new_content: str):
        db = next(get_db())
        try:
            note = db.query(Notas).filter(Notas.idNota == note_id).first()
            if not note:
                print("❌ No se encontró la nota para actualizar.")
                return None

            note.content = new_content
            db.commit()
            print(f"✔ Nota actualizada: ID: {note.idNota}, Nuevo contenido: {note.content}")
            return note
        except SQLAlchemyError as e:
            db.rollback()
            print("❌ Error al actualizar la nota:", str(e))
            return None
        finally:
            db.close()

