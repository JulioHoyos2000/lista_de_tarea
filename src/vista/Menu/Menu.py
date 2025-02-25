import sys
import os
import logging
from PyQt6 import uic
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTableWidgetItem, QWidget, QHBoxLayout, QPushButton, QMessageBox
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

def create_buttons_widget(row, callback):
    widget = QWidget()
    layout = QHBoxLayout(widget)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(5)

    btn_add = QPushButton("➕ Agregar", widget)
    btn_edit = QPushButton("⚙️ Editar", widget)
    btn_delete = QPushButton("🗑️ Eliminar", widget)

    btn_add.setFixedSize(70, 30)
    btn_edit.setFixedSize(65, 30)
    btn_delete.setFixedSize(70, 30)

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

        self.pushButton_2.clicked.connect(self.abrir_categoria)
        self.pushButton_3.clicked.connect(self.abrir_new_task)
        self.searchButton.clicked.connect(self.buscar_tareas)

        if self.comboBox.count() == 0 or self.comboBox.currentText() != "TODAS":
            self.comboBox.insertItem(0, "TODAS")
            self.comboBox.setCurrentIndex(0)

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

    def configurar_tabla(self):
        self.tableWidget.setColumnCount(7)
        self.tableWidget.verticalHeader().setDefaultSectionSize(45)
        self.tableWidget.setColumnWidth(6, 250)

    def cargar_categorias_combo(self):
        try:
            categorias = Categorias.listar_categorias()
            self.comboBox_2.clear()
            self.comboBox_2.addItem("TODAS")
            for categoria in categorias:
                self.comboBox_2.addItem(categoria.nombre)
        except Exception as e:
            logging.error(f"Error al cargar categorías: {e}")
            QMessageBox.critical(self, "Error", "No se pudieron cargar las categorías.")

    def buscar_tareas(self):
        texto = self.lineEdit.text().strip()
        if not texto:
            self.cargar_tareas()
            return

        try:
            tareas = Tareas.listar_tareas()
            tareas_filtradas = [t for t in tareas if texto.lower() in t["titulo"].lower()]

            if tareas_filtradas:
                self.actualizar_tabla_filtrada(tareas_filtradas)
            else:
                self.tableWidget.setRowCount(0)
                QMessageBox.information(self, "Búsqueda", "No se encontraron tareas con ese título.")
        except Exception as e:
            logging.error(f"Error en la búsqueda: {e}")
            QMessageBox.critical(self, "Error", f"Error al buscar tareas: {e}")

    def filtrar_tareas(self):
        try:
            tareas = Tareas.listar_tareas()
            prioridad = self.comboBox.currentText()
            categoria = self.comboBox_2.currentText()
            estado = self.comboBox_3.currentText()

            if prioridad != "TODAS":
                tareas = [t for t in tareas if t["prioridad"] == prioridad]
            if categoria != "TODAS":
                tareas = [t for t in tareas if (t["categoria"] or "").upper() == categoria.upper()]
            if estado != "TODAS":
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

                item_check = QTableWidgetItem()
                item_check.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
                item_check.setData(Qt.ItemDataRole.UserRole, tarea["idTarea"])
                item_check.setCheckState(
                    Qt.CheckState.Checked if tarea["estado"].upper() == "COMPLETADA" else Qt.CheckState.Unchecked
                )
                self.tableWidget.setItem(row, 0, item_check)

                self.tableWidget.setItem(row, 1, QTableWidgetItem(tarea["titulo"]))
                self.tableWidget.setItem(row, 2, QTableWidgetItem(tarea["categoria"] or ""))
                self.tableWidget.setItem(row, 3, QTableWidgetItem(tarea["prioridad"]))
                self.tableWidget.setItem(row, 4, QTableWidgetItem(tarea["estado"]))
                fecha_text = tarea["fecha"].strftime("%Y-%m-%d") if tarea["fecha"] else ""
                self.tableWidget.setItem(row, 5, QTableWidgetItem(fecha_text))

                button_widget = create_buttons_widget(row, self.handle_button_click)
                self.tableWidget.setCellWidget(row, 6, button_widget)

            self.tableWidget.blockSignals(False)
        except Exception as e:
            logging.error(f"Error al actualizar tabla: {e}")
            QMessageBox.critical(self, "Error", "Error al actualizar la tabla de tareas.")

    def cargar_tareas(self):
        try:
            tareas = Tareas.listar_tareas()
            self.actualizar_tabla_filtrada(tareas)
        except Exception as e:
            logging.error(f"Error al cargar tareas: {e}")
            QMessageBox.critical(self, "Error", "No se pudieron cargar las tareas.")

    def on_item_changed(self, item):
        if item.column() == 0:
            tarea_id = item.data(Qt.ItemDataRole.UserRole)
            if not tarea_id:
                return
            new_state = "COMPLETADA" if item.checkState() == Qt.CheckState.Checked else "PENDIENTE"
            actualizado = Tareas.editar_tarea(tarea_id, estado=new_state)
            if actualizado is None:
                QMessageBox.critical(self, "Error", "No se pudo actualizar el estado de la tarea.")
            else:
                self.tableWidget.blockSignals(True)
                self.tableWidget.setItem(item.row(), 4, QTableWidgetItem(new_state))
                self.tableWidget.blockSignals(False)
                logging.info(f"Tarea {tarea_id} actualizada a estado {new_state}")

    def handle_button_click(self, row, action):
        usuario_id = getattr(self.usuario, "id", "Desconocido")
        logging.info(f"Usuario ID: {usuario_id}")
        item = self.tableWidget.item(row, 0)
        tarea_id = item.data(Qt.ItemDataRole.UserRole) if item else None

        if action == "agregar":
            logging.info(f"Acción Agregar en la fila {row}")
            # Recuperar el título de la tarea de la columna 1
            task_title = self.tableWidget.item(row, 1).text()
            # Intentar obtener la nota asociada a la tarea.
            existing_note = NotasT.get_note_by_task(task_title)
            if existing_note:
                # Si existe, pasamos el id y el contenido ya guardado (sin mostrar mensaje de confirmación).
                self.notas_form_window = NotasForm(task_title=task_title,
                                                   note_id=existing_note.idNota,
                                                   existing_content=existing_note.content)
            else:
                # Si no existe, mostramos un mensaje y luego abrimos el formulario para crear la nota.
                QMessageBox.information(self, "Nota", "Creando nota")
                self.notas_form_window = NotasForm(task_title=task_title)
            self.notas_form_window.show()
        elif action == "editar":
            logging.info(f"Acción Editar en la fila {row}")
            tareas = Tareas.listar_tareas()
            tarea_data = next((t for t in tareas if t["idTarea"] == tarea_id), None)
            if tarea_data:
                self.editar_tarea_window = EditarTarea(tarea_data)
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
        self.cargar_categorias_combo()
