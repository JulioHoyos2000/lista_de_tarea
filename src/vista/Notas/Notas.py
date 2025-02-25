import sys
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QTextEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QDateEdit, QMessageBox
)
from PyQt6.QtCore import QDate
from src.logica.notas import NotasT

class NotasForm(QWidget):
    def __init__(self, task_title: str, note_id: str = None, existing_content: str = ""):

        super().__init__()
        self.task_title = task_title
        self.note_id = note_id
        self.initUI(existing_content)

    def initUI(self, existing_content: str):
        self.setWindowTitle("Notas")
        self.setStyleSheet("background-color: white;")

        # Labels
        label_titulo = QLabel("TITULO:")
        label_contenido = QLabel("CONTENIDO:")
        label_fecha = QLabel("FECHA:")

        # Input fields
        self.titulo_input = QLineEdit()
        self.titulo_input.setText(self.task_title)
        self.titulo_input.setReadOnly(True)
        self.contenido_input = QTextEdit()
        # If an existing note is found, fill the content field
        if self.note_id and existing_content:
            self.contenido_input.setText(existing_content)

        # Date field
        self.fecha_input = QDateEdit(calendarPopup=True)
        self.fecha_input.setDate(QDate.currentDate())
        self.fecha_input.setDisplayFormat("yyyy-MM-dd")

        # Buttons
        btn_guardar = QPushButton("GUARDAR")
        btn_guardar.setStyleSheet("background-color: #00BCD4; color: white; padding: 8px; border-radius: 4px;")
        btn_volver = QPushButton("VOLVER")
        btn_volver.setStyleSheet("background-color: #00BCD4; color: white; padding: 8px; border-radius: 4px;")

        # Layout configuration
        layout = QVBoxLayout()
        layout.addWidget(label_titulo)
        layout.addWidget(self.titulo_input)
        layout.addWidget(label_contenido)
        layout.addWidget(self.contenido_input)
        layout.addWidget(label_fecha)
        layout.addWidget(self.fecha_input)

        botones_layout = QHBoxLayout()
        botones_layout.addWidget(btn_guardar)
        botones_layout.addWidget(btn_volver)
        layout.addLayout(botones_layout)

        self.setLayout(layout)

        btn_guardar.clicked.connect(self.guardar_nota)
        btn_volver.clicked.connect(self.cerrar_formulario)

    def guardar_nota(self):
        task_title = self.titulo_input.text()
        content = self.contenido_input.toPlainText()
        fecha_str = self.fecha_input.date().toString("yyyy-MM-dd")
        try:
            created_at = datetime.strptime(fecha_str, "%Y-%m-%d")
        except ValueError:
            QMessageBox.critical(self, "Error", "Formato de fecha incorrecto.")
            return

        if self.note_id:
            note = NotasT.update_note(self.note_id, content)
            if note:
                QMessageBox.information(self, "Éxito", f"Nota actualizada exitosamente con ID: {note.idNota}")
                self.close()
            else:
                QMessageBox.critical(self, "Error", "No se pudo actualizar la nota.")
        else:
            note = NotasT.create_note(task_title=task_title, content=content, created_at=created_at)
            if note:
                QMessageBox.information(self, "Éxito", f"Nota guardada exitosamente con ID: {note.idNota}")
                self.close()
            else:
                QMessageBox.critical(self, "Error", "No se pudo guardar la nota.")

    def cerrar_formulario(self):
        self.close()

