import sys
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QLabel, QLineEdit, QComboBox, QVBoxLayout,
    QPushButton, QHBoxLayout, QDateEdit, QMessageBox
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal
from src.logica.tareas import Tareas
from src.BaseDatos.Conexion import get_db
from src.logica.categorias import Categorias

class EditarTarea(QMainWindow):
    tarea_guardada = pyqtSignal(dict)

    def __init__(self, tarea_data, user_id: str):
        super().__init__()
        self.tarea_data = tarea_data
        self.user_id = user_id
        self.db = next(get_db())
        self.setWindowTitle("Editar Tarea")
        self.setFixedWidth(330)
        self.initUI()

    def initUI(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)

        # Campo de título
        self.titulo_input = self.create_form_field("NOMBRE:", "✏️", main_layout)
        self.titulo_input.setText(self.tarea_data["titulo"])

        # Combo de categorías
        self.categoria_combo = QComboBox()
        main_layout.addWidget(QLabel("CATEGORÍA:"))
        main_layout.addWidget(self.categoria_combo)
        self.populate_categoria_combo()
        index = self.categoria_combo.findText(self.tarea_data["categoria"], Qt.MatchFlag.MatchFixedString)
        if index >= 0:
            self.categoria_combo.setCurrentIndex(index)

        # Combo de prioridad
        self.prioridad_combo = self.create_combo_field("PRIORIDAD:", ["Alta", "Media", "Baja"], main_layout)
        self.prioridad_combo.setCurrentText(self.tarea_data["prioridad"])

        # Combo de estado
        self.estado_combo = self.create_combo_field("ESTADO:", ["Pendiente", "En Proceso", "Completada"], main_layout)
        self.estado_combo.setCurrentText(self.tarea_data["estado"])

        # Campo de fecha
        date_label = QLabel("FECHA:")
        main_layout.addWidget(date_label)
        self.date_edit = QDateEdit(calendarPopup=True)
        fecha_val = self.tarea_data["fecha"]
        if isinstance(fecha_val, str):
            fecha_qdate = QDate.fromString(fecha_val, "yyyy-MM-dd")
            if fecha_qdate.isValid():
                self.date_edit.setDate(fecha_qdate)
            else:
                self.date_edit.setDate(QDate.currentDate())
        elif hasattr(fecha_val, "strftime"):
            fecha_str = fecha_val.strftime("%Y-%m-%d")
            fecha_qdate = QDate.fromString(fecha_str, "yyyy-MM-dd")
            if fecha_qdate.isValid():
                self.date_edit.setDate(fecha_qdate)
            else:
                self.date_edit.setDate(QDate.currentDate())
        else:
            self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        main_layout.addWidget(self.date_edit)

        # Botones de guardar y volver
        button_layout = QHBoxLayout()
        save_btn = QPushButton("GUARDAR")
        save_btn.clicked.connect(self.guardar_cambios)
        button_layout.addWidget(save_btn)

        back_btn = QPushButton("VOLVER")
        back_btn.clicked.connect(self.close)
        button_layout.addWidget(back_btn)
        main_layout.addLayout(button_layout)

    def create_form_field(self, label_text, emoji, layout):
        layout.addWidget(QLabel(label_text))
        line_edit = QLineEdit()
        line_edit.setPlaceholderText(f"{emoji} Escribir aquí...")
        layout.addWidget(line_edit)
        return line_edit

    def create_combo_field(self, label_text, items, layout):
        layout.addWidget(QLabel(label_text))
        combo = QComboBox()
        combo.addItems(items)
        layout.addWidget(combo)
        return combo

    def populate_categoria_combo(self):
        self.categoria_combo.clear()
        try:
            categorias = Categorias.listar_categorias(self.user_id)
            for cat in categorias:
                self.categoria_combo.addItem(cat.nombre)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudieron cargar las categorías: {e}")

    def guardar_cambios(self):
        try:
            tarea_actualizada = {
                "idTarea": self.tarea_data["idTarea"],  # Conserva el ID original
                "titulo": self.titulo_input.text().strip(),
                "categoria": self.categoria_combo.currentText(),
                "prioridad": self.prioridad_combo.currentText(),
                "estado": self.estado_combo.currentText(),
                "fecha": self.date_edit.date().toString("yyyy-MM-dd")
            }

            if not tarea_actualizada["titulo"]:
                QMessageBox.warning(self, "Campos vacíos", "El campo de título no puede estar vacío.")
                return

            # Recuperar la categoría seleccionada usando el user_id
            categorias = Categorias.listar_categorias(self.user_id)
            id_categoria = None
            for cat in categorias:
                if cat.nombre == tarea_actualizada["categoria"]:
                    id_categoria = cat.idCat
                    break

            actualizado = Tareas.editar_tarea(
                tarea_actualizada["idTarea"],
                titulo=tarea_actualizada["titulo"],
                id_categoria=id_categoria,
                prioridad=tarea_actualizada["prioridad"],
                estado=tarea_actualizada["estado"],
                fecha=tarea_actualizada["fecha"]
            )

            if not actualizado:
                QMessageBox.critical(self, "Error", "No se pudo actualizar la tarea en la base de datos.")
                return

            QMessageBox.information(self, "Éxito", "✅ Tarea editada correctamente")
            self.tarea_guardada.emit(tarea_actualizada)
            self.close()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al guardar los cambios: {e}")

    def closeEvent(self, event):
        if hasattr(self, "db") and self.db:
            self.db.close()
        event.accept()