import sys
import os
import logging
from PyQt6 import uic
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTableWidgetItem, QWidget, QHBoxLayout,
    QPushButton, QMessageBox, QComboBox, QStyledItemDelegate, QStyle
)
from PyQt6.QtCore import Qt
from src.vista.Categorias.categoria import CrearCategoria
from src.vista.Tareas.CrearTarea import CategoryForm
from src.vista.Tareas.EditarTarea import EditarTarea
from src.logica.tareas import Tareas
from src.logica.categorias import Categorias
from src.vista.Notas.Notas import NotasForm
from src.logica.notas import NotasT

logging.basicConfig(level=logging.INFO)

# Delegate to center the content of the cell and remove the focus rectangle
class CenteredDelegate(QStyledItemDelegate):
    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        # Center the content of the cell.
        option.displayAlignment = Qt.AlignmentFlag.AlignCenter

    def paint(self, painter, option, index):
        option.state &= ~QStyle.StateFlag.State_HasFocus
        super().paint(painter, option, index)

def create_buttons_widget(row, callback):
    widget = QWidget()
    layout = QHBoxLayout(widget)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(5)

    # Create buttons with default styles: white background, black text.
    # On hover/pressed, change background and show white text.
    btn_add = QPushButton("➕ Agregar", widget)
    btn_edit = QPushButton("⚙️ Editar", widget)
    btn_delete = QPushButton("🗑️ Eliminar", widget)

    btn_add.setFixedSize(70, 30)
    btn_edit.setFixedSize(65, 30)
    btn_delete.setFixedSize(70, 30)

    # Set style sheets for each button.
    btn_add.setStyleSheet("""
QPushButton {
background-color: white;
color: black;
border: 1px solid #ccc;
}
QPushButton:hover {
background-color: #4CAF50; /* green */
color: white;
}
QPushButton:pressed {
background-color: #388E3C; /* darker green */
color: white;
}
    """)

    btn_edit.setStyleSheet("""
QPushButton {
background-color: white;
color: black;
border: 1px solid #ccc;
}
QPushButton:hover {
background-color: #2196F3; /* blue */
color: white;
}
QPushButton:pressed {
background-color: #1976D2; /* darker blue */
color: white;
}
    """)

    btn_delete.setStyleSheet("""
QPushButton {
background-color: white;
color: black;
border: 1px solid #ccc;
}
QPushButton:hover {
background-color: #f44336; /* red */
color: white;
}
QPushButton:pressed {
background-color: #d32f2f; /* darker red */
color: white;
}
    """)

    # Connect signals to callback
    btn_add.clicked.connect(lambda: callback(row, "agregar"))
    btn_edit.clicked.connect(lambda: callback(row, "editar"))
    btn_delete.clicked.connect(lambda: callback(row, "eliminar"))

    layout.addWidget(btn_add)
    layout.addWidget(btn_edit)
    layout.addWidget(btn_delete)
    return widget

class MainWindow(QMainWindow):
    def __init__(self, usuario=None):
        super().__init__()
        self.usuario = usuario
        logging.info(f"Usuario logueado: {self.usuario}")
        ui_path = os.path.join(os.path.dirname(__file__), 'main.ui')
        uic.loadUi(ui_path, self)

        if hasattr(self, 'menubar'):
            self.setMenuBar(self.menubar)

        # Button connections
        self.pushButton_2.clicked.connect(self.abrir_categoria)
        self.pushButton_3.clicked.connect(self.abrir_new_task)
        self.searchButton.clicked.connect(self.buscar_tareas)

        # Initialize comboboxes with placeholders
        self.init_comboboxes()

        self.comboBox.currentIndexChanged.connect(self.filtrar_tareas)
        self.comboBox_2.currentIndexChanged.connect(self.filtrar_tareas)
        self.comboBox_3.currentIndexChanged.connect(self.filtrar_tareas)

        self.tableWidget.itemChanged.connect(self.on_item_changed)

        self.configurar_tabla()
        self.cargar_categorias_combo()
        self.cargar_tareas()

        self.categoria_window = None
        self.new_task_window = None
        self.editar_tarea_window = None
        self.notas_form_window = None

    def init_comboboxes(self):
        # self.comboBox: PRIORIDAD
        self.comboBox.clear()
        self.comboBox.addItem("PRIORIDAD")
        self.comboBox.addItems(["Alta", "Media", "Baja"])
        self.comboBox.setCurrentIndex(0)
        # self.comboBox_2: CATEGORÍA
        self.comboBox_2.clear()
        self.comboBox_2.addItem("CATEGORÍA")
        self.comboBox_2.setCurrentIndex(0)
        # self.comboBox_3: ESTADO
        self.comboBox_3.clear()
        self.comboBox_3.addItem("ESTADO")
        self.comboBox_3.addItems(["Pendiente", "En Proceso", "Completada"])
        self.comboBox_3.setCurrentIndex(0)

    def configurar_tabla(self):
        self.tableWidget.setColumnCount(7)
        self.tableWidget.verticalHeader().setDefaultSectionSize(45)
        self.tableWidget.setColumnWidth(6, 250)
        # Set a delegate for the checkbox column (column 0) to center content and remove focus drawing.
        delegate = CenteredDelegate(self.tableWidget)
        self.tableWidget.setItemDelegateForColumn(0, delegate)

    def cargar_categorias_combo(self):
        try:
            # Save current selection and reset placeholder "CATEGORÍA"
            current_selection = self.comboBox_2.currentText()
            self.comboBox_2.clear()
            self.comboBox_2.addItem("CATEGORÍA")
            usuario_id = getattr(self.usuario, "id", None)
            categorias = Categorias.listar_categorias(usuario_id) if usuario_id else []
            for categoria in categorias:
                self.comboBox_2.addItem(categoria.nombre)
            # Restore previous selection if not placeholder
            if current_selection and current_selection != "CATEGORÍA":
                index = self.comboBox_2.findText(current_selection)
                if index >= 0:
                    self.comboBox_2.setCurrentIndex(index)
                else:
                    self.comboBox_2.setCurrentIndex(0)
            logging.info("ComboBox_2 actualizado con las categorías actuales")
        except Exception as e:
            logging.error(f"Error al cargar categorías: {e}")
            QMessageBox.critical(self, "Error", "No se pudieron cargar las categorías.")

    def buscar_tareas(self):
        texto = self.lineEdit.text().strip()
        usuario_id = getattr(self.usuario, "id", None)
        if not texto:
            self.cargar_tareas()
            return
        try:
            # Filter tasks by title and user
            tareas = Tareas.buscar_por_titulo(texto, usuario_id) if usuario_id else []
            if tareas:
                self.actualizar_tabla_filtrada(tareas)
            else:
                self.tableWidget.setRowCount(0)
                QMessageBox.information(self, "Búsqueda", "No se encontraron tareas con ese título.")
        except Exception as e:
            logging.error(f"Error en la búsqueda: {e}")
            QMessageBox.critical(self, "Error", f"Error al buscar tareas: {e}")

    def filtrar_tareas(self):
        try:
            usuario_id = getattr(self.usuario, "id", None)
            tareas = Tareas.listar_tareas(usuario_id) if usuario_id else []
            # Filter by priority if value is not placeholder
            prioridad = self.comboBox.currentText()
            if prioridad != "PRIORIDAD":
                tareas = [t for t in tareas if t["prioridad"] == prioridad]
            # Filter by category if value is not placeholder
            categoria = self.comboBox_2.currentText()
            if categoria != "CATEGORÍA":
                tareas = [t for t in tareas if (t["categoria"] or "").upper() == categoria.upper()]
            # Filter by state if value is not placeholder
            estado = self.comboBox_3.currentText()
            if estado != "ESTADO":
                tareas = [t for t in tareas if t["estado"].upper() == estado.upper()]

            self.actualizar_tabla_filtrada(tareas)
        except Exception as e:
            logging.error(f"Error al filtrar tareas: {e}")
            QMessageBox.critical(self, "Error", "Error al aplicar filtros en las tareas.")

    def actualizar_tabla_filtrada(self, tareas):
        try:
            self.tableWidget.blockSignals(True)
            self.tableWidget.setRowCount(0)
            for row, tarea in enumerate(tareas):
                self.tableWidget.insertRow(row)
                # Checkbox column (column 0)
                item_check = QTableWidgetItem()
                item_check.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
                item_check.setData(Qt.ItemDataRole.UserRole, tarea["idTarea"])
                item_check.setCheckState(
                    Qt.CheckState.Checked if tarea["estado"].upper() == "COMPLETADA" else Qt.CheckState.Unchecked
                )
                item_check.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.tableWidget.setItem(row, 0, item_check)

                # Title column (column 1)
                title_item = QTableWidgetItem(tarea["titulo"])
                title_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.tableWidget.setItem(row, 1, title_item)

                # Category column (column 2)
                cat_item = QTableWidgetItem(tarea["categoria"] or "")
                cat_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.tableWidget.setItem(row, 2, cat_item)

                # Priority column (column 3)
                priority_item = QTableWidgetItem(tarea["prioridad"])
                priority_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.tableWidget.setItem(row, 3, priority_item)

                # State column (column 4)
                state_item = QTableWidgetItem(tarea["estado"])
                state_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.tableWidget.setItem(row, 4, state_item)

                # Date column (column 5)
                fecha_text = tarea["fecha"].strftime("%Y-%m-%d") if tarea["fecha"] else ""
                date_item = QTableWidgetItem(fecha_text)
                date_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.tableWidget.setItem(row, 5, date_item)

                # Actions column (column 6)
                button_widget = create_buttons_widget(row, self.handle_button_click)
                self.tableWidget.setCellWidget(row, 6, button_widget)
            self.tableWidget.blockSignals(False)
        except Exception as e:
            logging.error(f"Error al actualizar tabla: {e}")
            QMessageBox.critical(self, "Error", "Error al actualizar la tabla de tareas.")

    def cargar_tareas(self):
        try:
            usuario_id = getattr(self.usuario, "id", None)
            tareas = Tareas.listar_tareas(usuario_id) if usuario_id else []
            if not tareas:
                QMessageBox.information(self, "Bienvenido", "Bienvenido al APP TODO-LIST")
            self.actualizar_tabla_filtrada(tareas)
        except Exception as e:
            logging.error(f"Error al cargar tareas: {e}")
            QMessageBox.critical(self, "Error", "No se pudieron cargar las tareas.")

    def on_item_changed(self, item):
        if item.column() == 0:
            tarea_id = item.data(Qt.ItemDataRole.UserRole)
            if not tarea_id:
                return
            new_state = "Completada" if item.checkState() == Qt.CheckState.Checked else "Pendiente"
            actualizado = Tareas.editar_tarea(tarea_id, estado=new_state)
            if actualizado is None:
                QMessageBox.critical(self, "Error", "No se pudo actualizar el estado de la tarea.")
            else:
                # Create a new QTableWidgetItem with centered text for the state
                new_item = QTableWidgetItem(new_state)
                new_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.tableWidget.blockSignals(True)
                self.tableWidget.setItem(item.row(), 4, new_item)
                self.tableWidget.blockSignals(False)
                logging.info(f"Tarea {tarea_id} actualizada a estado {new_state}")

    def handle_button_click(self, row, action):
        usuario_id = getattr(self.usuario, "id", "Desconocido")
        logging.info(f"Usuario ID: {usuario_id}")
        item = self.tableWidget.item(row, 0)
        tarea_id = item.data(Qt.ItemDataRole.UserRole) if item else None

        if action == "agregar":
            logging.info(f"Acción Agregar en la fila {row}")
            task_title = self.tableWidget.item(row, 1).text()
            existing_note = NotasT.get_note_by_task(task_title)
            if existing_note:
                self.notas_form_window = NotasForm(
                    task_title=task_title,
                    note_id=existing_note.idNota,
                    existing_content=existing_note.content
                )
            else:
                QMessageBox.information(self, "Nota", "Creando nota")
                self.notas_form_window = NotasForm(task_title=task_title)
            self.notas_form_window.show()
        elif action == "editar":
            logging.info(f"Acción Editar en la fila {row}")
            usuario_id = getattr(self.usuario, "id", None)
            tareas = Tareas.listar_tareas(usuario_id) if usuario_id else []
            tarea_data = next((t for t in tareas if t["idTarea"] == tarea_id), None)
            if tarea_data:
                self.editar_tarea_window = EditarTarea(tarea_data, usuario_id)
                self.editar_tarea_window.tarea_guardada.connect(self.actualizar_tareas)
                self.editar_tarea_window.show()
            else:
                QMessageBox.warning(self, "Error", "No se encontró la tarea para editar.")
        elif action == "eliminar":
            logging.info(f"Acción Eliminar en la fila {row}")
            reply = QMessageBox.question(
                self, "Confirmar eliminación",
                "¿Estás seguro de que deseas eliminar esta tarea?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                eliminado = Tareas.eliminar_tarea(tarea_id)
                if eliminado:
                    QMessageBox.information(self, "Éxito", "✅ Tarea eliminada correctamente")
                    self.cargar_tareas()
                else:
                    QMessageBox.critical(self, "Error", "No se pudo eliminar la tarea.")

    def abrir_categoria(self):
        usuario_id = getattr(self.usuario, "id", None)
        if self.categoria_window is None:
            self.categoria_window = CrearCategoria(usuario_id=usuario_id, parent=self)
            self.categoria_window.categoria_creada.connect(self.cargar_categorias_combo)
            if hasattr(self.categoria_window, "categoria_editada"):
                self.categoria_window.categoria_editada.connect(self.cargar_categorias_combo)
            if hasattr(self.categoria_window, "categoria_eliminada"):
                self.categoria_window.categoria_eliminada.connect(self.cargar_categorias_combo)
        self.categoria_window.show()

    def abrir_new_task(self):
        usuario_id = getattr(self.usuario, "id", None)
        if not usuario_id:
            QMessageBox.warning(self, "Error", "ID de usuario no encontrado.")
            return
        if self.new_task_window is None:
            self.new_task_window = CategoryForm(user_id=usuario_id)
            self.new_task_window.tarea_guardada.connect(self.actualizar_tareas)
        self.new_task_window.show()

    def actualizar_tareas(self, nueva_tarea):
        logging.info("Nueva tarea guardada o actualizada, actualizando la lista de tareas...")
        self.cargar_tareas()