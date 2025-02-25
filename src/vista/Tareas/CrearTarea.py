import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QLineEdit,
    QComboBox, QVBoxLayout, QPushButton, QHBoxLayout, QDateEdit, QMessageBox
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal
from src.logica.tareas import Tareas
from src.logica.categorias import Categorias
from src.BaseDatos.Conexion import get_db

class CategoryForm(QMainWindow):
    tarea_guardada = pyqtSignal(dict)

    def __init__(self, user_id: str):
        super().__init__()
        self.user_id = user_id
        self.setFixedWidth(330)
        self.categorias_map = {}
        self.init_ui()
        # Initially load categories.
        self.cargar_categorias()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)

        # Título de la tarea
        self.titulo_input = self.create_form_field("TITULO:", "✏️", main_layout)

        # Combo de categoría
        self.categoria_combo = self.create_combo_field("CATEGORÍA:", [], main_layout)
        # Combo de prioridad
        self.prioridad_combo = self.create_combo_field("PRIORIDAD:", ["Alta", "Media", "Baja"], main_layout)
        # Combo de estado
        self.estado_combo = self.create_combo_field("ESTADO:", ["Pendiente", "En Proceso", "Completada"], main_layout)

        # Campo de fecha
        date_label = QLabel("FECHA:")
        main_layout.addWidget(date_label)
        self.date_edit = QDateEdit(calendarPopup=True)
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        main_layout.addWidget(self.date_edit)

        # Botones de acción
        button_layout = QHBoxLayout()
        save_btn = QPushButton("GUARDAR")
        save_btn.clicked.connect(self.guardar_tarea)
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

    def cargar_categorias(self):
        try:
            # Clear combo and internal mapping before reloading
            self.categoria_combo.clear()
            self.categorias_map.clear()
            categorias = Categorias.listar_categorias()
            nombres_categorias = []
            for cat in categorias:
                nombres_categorias.append(cat.nombre)
                self.categorias_map[cat.nombre] = cat.idCat
            self.categoria_combo.addItems(nombres_categorias)
            if not nombres_categorias:
                print("No se encontraron categorías. El combo estará vacío.")
        except Exception as e:
            print(f"Error al cargar categorías: {e}")
            QMessageBox.critical(self, "Error", "No se pudieron cargar las categorías.")

    def guardar_tarea(self):
        try:
            print("💾 Iniciando el proceso para guardar la tarea...")
            if not self.titulo_input.text().strip():
                raise ValueError("❗ El título de la tarea es obligatorio.")
            nueva_tarea = {
                "titulo": self.titulo_input.text().strip(),
                "categoria": self.categoria_combo.currentText(),
                "prioridad": self.prioridad_combo.currentText(),
                "estado": self.estado_combo.currentText(),
                "fecha": self.date_edit.date().toString("yyyy-MM-dd"),
                "user_id": self.user_id
            }
            print("Datos de tarea a guardar:", nueva_tarea)
            id_categoria = self.categorias_map.get(nueva_tarea["categoria"], None)
            tarea_creada = Tareas.crear_tarea(
                id_usuario=nueva_tarea["user_id"],
                titulo=nueva_tarea["titulo"],
                id_categoria=id_categoria,
                prioridad=nueva_tarea["prioridad"],
                estado=nueva_tarea["estado"],
                fecha=nueva_tarea["fecha"]
            )
            nueva_tarea["id"] = tarea_creada.idTarea if hasattr(tarea_creada, "idTarea") else None

            QMessageBox.information(self, "Éxito", "✅ Tarea guardada exitosamente.")
            self.tarea_guardada.emit(nueva_tarea)
            self.limpiar_formulario()
            self.close()

        except ValueError as ve:
            QMessageBox.warning(self, "Campos Obligatorios", str(ve))
        except Exception as e:
            print(f"Error: {e}")
            QMessageBox.critical(self, "Error Inesperado", f"❌ Error inesperado: {str(e)}")

    def limpiar_formulario(self):
        self.titulo_input.clear()
        self.categoria_combo.setCurrentIndex(0)
        self.prioridad_combo.setCurrentIndex(0)
        self.estado_combo.setCurrentIndex(0)
        self.date_edit.setDate(QDate.currentDate())

    def closeEvent(self, event):
        unsaved_changes = (
            self.titulo_input.text().strip() or
            self.categoria_combo.currentIndex() != 0 or
            self.prioridad_combo.currentIndex() != 0 or
            self.estado_combo.currentIndex() != 0 or
            self.date_edit.date() != QDate.currentDate()
        )
        if unsaved_changes:
            reply = QMessageBox.question(
                self, "Confirmar Cierre",
                "Tienes cambios sin guardar. ¿Deseas salir sin guardar?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

    def showEvent(self, event):
        # Refresh categories every time the form is shown.
        self.cargar_categorias()
        super().showEvent(event)

