import sys
import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit,
    QTableWidget, QTableWidgetItem, QApplication, QHBoxLayout, QDialog,
    QHeaderView, QMessageBox, QDateEdit
)
from PyQt6.QtCore import Qt, pyqtSignal, QDate
from src.BaseDatos.Conexion import get_db
from src.logica.categorias import Categorias

class CrearCategoria(QMainWindow):
    categoria_creada = pyqtSignal(dict)

    def __init__(self, usuario_id=None, parent=None):
        super().__init__(parent)
        self.usuario_id = usuario_id
        self.setWindowTitle("Gestión de Categorías")
        self.resize(320, 250)
        self.initUI()
        self.cargar_categorias()

    def initUI(self):
        main_widget = QWidget(self)
        main_layout = QVBoxLayout(main_widget)

        self.btnCrear = QPushButton("+ Crear Categoría")
        self.btnCrear.setStyleSheet(
            "background-color: orange; color: white; font-weight: bold; padding: 5px; border-radius: 5px;"
        )
        self.btnCrear.clicked.connect(self.abrir_formulario_categoria)
        main_layout.addWidget(self.btnCrear)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Nombre", "Fecha", "Acciones"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(2, 150)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        main_layout.addWidget(self.table)

        self.setCentralWidget(main_widget)

    def abrir_formulario_categoria(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Crear Categoría")
        dialog.setFixedSize(300, 250)
        layout = QVBoxLayout(dialog)

        layout.addWidget(QLabel("Nombre:"))
        self.input_nombre = QLineEdit()
        layout.addWidget(self.input_nombre)

        layout.addWidget(QLabel("Fecha:"))
        self.input_fecha = QDateEdit(calendarPopup=True)
        self.input_fecha.setDisplayFormat("yyyy-MM-dd")
        self.input_fecha.setDate(QDate.currentDate())
        layout.addWidget(self.input_fecha)

        btn_guardar = QPushButton("Guardar")
        btn_guardar.setStyleSheet(
            "background-color: #5bc0de; color: white; border: none; padding: 6px 12px; border-radius: 4px;"
        )
        btn_guardar.clicked.connect(lambda: self.guardar_categoria(dialog))
        layout.addWidget(btn_guardar)

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.clicked.connect(dialog.reject)
        layout.addWidget(btn_cancelar)

        dialog.exec()

    def guardar_categoria(self, dialog):
        nombre = self.input_nombre.text().strip()
        if not nombre:
            QMessageBox.warning(self, "Error", "El nombre es obligatorio.")
            return

        fecha_str = self.input_fecha.date().toString("yyyy-MM-dd")
        categoria = Categorias.create_category(nombre, self.usuario_id)
        if not categoria:
            QMessageBox.warning(self, "Error", "La categoría ya existe o ocurrió un error.")
            return

        categoria_data = {
            "idCat": categoria.idCat,
            "nombre": categoria.nombre,
            "fecha": categoria.fecha.strftime("%Y-%m-%d") if categoria.fecha else ""
        }

        self.agregar_categoria_a_tabla(categoria_data)
        # Emit the signal with the new category data
        self.categoria_creada.emit(categoria_data)
        dialog.accept()

    def agregar_categoria_a_tabla(self, categoria_data):
        row = self.table.rowCount()
        self.table.insertRow(row)

        item_nombre = QTableWidgetItem(categoria_data['nombre'])
        item_nombre.setData(Qt.ItemDataRole.UserRole, categoria_data['idCat'])
        self.table.setItem(row, 0, item_nombre)

        self.table.setItem(row, 1, QTableWidgetItem(categoria_data['fecha']))

        btn_editar = QPushButton("Editar")
        btn_editar.setStyleSheet(
            "background-color: #5bc0de; color: white; font-weight: bold; padding: 3px; border-radius: 5px;"
        )
        btn_eliminar = QPushButton("Eliminar")
        btn_eliminar.setStyleSheet(
            "background-color: red; color: white; font-weight: bold; padding: 3px; border-radius: 5px;"
        )
        btn_editar.clicked.connect(lambda _, r=row: self.editar_categoria(r))
        btn_eliminar.clicked.connect(lambda _, r=row: self.eliminar_categoria(r))

        acciones_widget = QWidget()
        acciones_layout = QHBoxLayout(acciones_widget)
        acciones_layout.setContentsMargins(0, 0, 0, 0)
        acciones_layout.addWidget(btn_editar)
        acciones_layout.addWidget(btn_eliminar)
        self.table.setCellWidget(row, 2, acciones_widget)

    def cargar_categorias(self):
        self.table.setRowCount(0)
        categorias = Categorias.listar_categorias()
        for cat in categorias:
            categoria_data = {
                "idCat": cat.idCat,
                "nombre": cat.nombre,
                "fecha": cat.fecha.strftime("%Y-%m-%d") if cat.fecha else ""
            }
            self.agregar_categoria_a_tabla(categoria_data)

    def editar_categoria(self, row):
        item = self.table.item(row, 0)
        if item is None:
            return
        id_cat = item.data(Qt.ItemDataRole.UserRole)
        nombre = item.text()
        fecha = self.table.item(row, 1).text()

        dialog = QDialog(self)
        dialog.setWindowTitle("Editar Categoría")
        dialog.setFixedSize(300, 250)
        layout = QVBoxLayout(dialog)

        layout.addWidget(QLabel("Nombre:"))
        self.input_nombre_editar = QLineEdit(nombre)
        layout.addWidget(self.input_nombre_editar)

        layout.addWidget(QLabel("Fecha:"))
        self.input_fecha_editar = QDateEdit(calendarPopup=True)
        self.input_fecha_editar.setDisplayFormat("yyyy-MM-dd")
        self.input_fecha_editar.setDate(QDate.fromString(fecha, "yyyy-MM-dd"))
        layout.addWidget(self.input_fecha_editar)

        btn_guardar = QPushButton("Guardar")
        btn_guardar.setStyleSheet(
            "background-color: #5bc0de; color: white; border: none; padding: 6px 12px; border-radius: 4px;"
        )
        btn_guardar.clicked.connect(lambda: self.guardar_editar(id_cat, row, dialog))
        layout.addWidget(btn_guardar)

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.clicked.connect(dialog.reject)
        layout.addWidget(btn_cancelar)

        dialog.exec()

    def guardar_editar(self, id_cat, row, dialog):
        nombre = self.input_nombre_editar.text().strip()
        if not nombre:
            QMessageBox.warning(self, "Error", "El nombre es obligatorio.")
            return

        nueva_fecha = self.input_fecha_editar.date().toString("yyyy-MM-dd")

        confirm = QMessageBox.question(
            self,
            "Confirmar Edición",
            f"¿Seguro que quieres editar la categoría {id_cat}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return

        categoria = Categorias.edit_category(id_cat, nombre)
        if not categoria:
            QMessageBox.warning(self, "Error", "No se encontró la categoría.")
            return

        new_item = QTableWidgetItem(nombre)
        new_item.setData(Qt.ItemDataRole.UserRole, id_cat)
        self.table.setItem(row, 0, new_item)
        self.table.setItem(row, 1, QTableWidgetItem(nueva_fecha))
        dialog.accept()
        QMessageBox.information(self, "Éxito", "Categoría editada con éxito.")

    def eliminar_categoria(self, row):
        respuesta = QMessageBox.question(
            self,
            "Confirmar Eliminación",
            "¿Seguro que quieres eliminar esta categoría?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if respuesta == QMessageBox.StandardButton.Yes:
            item = self.table.item(row, 0)
            if not item:
                return
            id_cat = item.data(Qt.ItemDataRole.UserRole)
            eliminado = Categorias.delete_category(id_cat)
            if eliminado:
                self.table.removeRow(row)
                QMessageBox.information(self, "Éxito", "Categoría eliminada.")
            else:
                QMessageBox.warning(self, "Error", "No se pudo eliminar la categoría.")

