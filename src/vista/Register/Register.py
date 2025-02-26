from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QCheckBox,
    QApplication,
    QMessageBox
)
from PyQt6.QtGui import QFont, QIcon, QPixmap
from PyQt6.QtCore import Qt, QSize
import os

# Importar la lógica de usuarios
from src.logica.usuarios import Usuarios
# Importar el menú principal
from src.vista.Menu.Menu import MainWindow

class RegisterWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Create an Account")
        self.setup_ui()

    def setup_ui(self):
        main_layout = QHBoxLayout(self)

        # --- Left Side (Image and Text) ---
        left_layout = QVBoxLayout()

        # --- Image Loading ---
        image_label = QLabel()
        image_path = r"C:\Users\USUARIO\IdeaProjects\lista_de_tarea\src\Recursos\Screenshot 2025-02-25 010219.png"
        pixmap = QPixmap(image_path)
        if pixmap.isNull():
            print(f"Error: Could not load image at {image_path}")
        else:
            scaled_pixmap = pixmap.scaled(
                400, 300, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
            )
            image_label.setPixmap(scaled_pixmap)
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(image_label)

        # --- Right Side (Form) ---
        right_layout = QVBoxLayout()

        # --- Top Bar ---
        top_bar_layout = QHBoxLayout()
        logo_placeholder = QLabel("LISTA-TAREAS")
        logo_placeholder.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        top_bar_layout.addWidget(logo_placeholder)
        top_bar_layout.addStretch()
        right_layout.addLayout(top_bar_layout)

        # --- Create Account Title ---
        title_label = QLabel("Create an account")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        right_layout.addWidget(title_label)

        # --- Login Label with Hyperlink ---
        login_label = QLabel("Already have an account? <a href='#'>Log in</a>")
        login_label.setFont(QFont("Arial", 10))
        login_label.setStyleSheet("color: gray;")
        login_label.setTextFormat(Qt.TextFormat.RichText)
        login_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        login_label.setOpenExternalLinks(True)
        right_layout.addWidget(login_label)

        # --- Form Fields ---
        # Name and Last Name in one row
        name_layout = QHBoxLayout()

        self.first_name_input = QLineEdit()
        self.first_name_input.setPlaceholderText("Name")
        first_name_icon_path = r"C:\Users\USUARIO\IdeaProjects\lista_de_tarea\src\Recursos\icons8-user-24.png"
        first_name_icon = QIcon(first_name_icon_path)
        if not first_name_icon.isNull():
            self.first_name_input.addAction(first_name_icon, QLineEdit.ActionPosition.LeadingPosition)
        else:
            print(f"Error: Could not load icon at {first_name_icon_path}")
        name_layout.addWidget(self.first_name_input)

        self.last_name_input = QLineEdit()
        self.last_name_input.setPlaceholderText("Last name")
        last_name_icon_path = r"C:\Users\USUARIO\IdeaProjects\lista_de_tarea\src\Recursos\icons8-user-24.png"
        last_name_icon = QIcon(last_name_icon_path)
        if not last_name_icon.isNull():
            self.last_name_input.addAction(last_name_icon, QLineEdit.ActionPosition.LeadingPosition)
        else:
            print(f"Error: Could not load icon at {last_name_icon_path}")
        name_layout.addWidget(self.last_name_input)
        right_layout.addLayout(name_layout)

        # Email Input with icon
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")
        email_icon_path = r"C:\Users\USUARIO\IdeaProjects\lista_de_tarea\src\Recursos\icons8-email-24.png"
        email_icon = QIcon(email_icon_path)
        if not email_icon.isNull():
            self.email_input.addAction(email_icon, QLineEdit.ActionPosition.LeadingPosition)
        else:
            print(f"Error: Could not load icon at {email_icon_path}")
        right_layout.addWidget(self.email_input)

        # Password Input with icon
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        password_icon_path = r"C:\Users\USUARIO\IdeaProjects\lista_de_tarea\src\Recursos\icons8-password-24.png"
        password_icon = QIcon(password_icon_path)
        if not password_icon.isNull():
            self.password_input.addAction(password_icon, QLineEdit.ActionPosition.LeadingPosition)
        else:
            print(f"Error: Could not load icon at {password_icon_path}")
        right_layout.addWidget(self.password_input)

        # --- Terms and Conditions ---
        self.terms_checkbox = QCheckBox("I agree to the Terms & Conditions")
        right_layout.addWidget(self.terms_checkbox)

        # --- Create Account Button ---
        self.create_account_button = QPushButton("Create account")
        self.create_account_button.setStyleSheet(
            "background-color: #800080; color: white; padding: 10px; border-radius: 5px;"
        )
        self.create_account_button.clicked.connect(self.register_user)
        right_layout.addWidget(self.create_account_button)

        # --- Or Register With ---
        or_label = QLabel("Or register with")
        or_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(or_label)

        # --- Social Buttons (with Icons) ---
        social_buttons_layout = QHBoxLayout()

        # Google Button with centered icon and text, and with border
        google_button = QPushButton()
        google_icon_path = r"C:\Users\USUARIO\IdeaProjects\lista_de_tarea\src\Recursos\google.png"
        google_icon = QIcon(google_icon_path)
        if google_icon.isNull():
            print(f"Error loading google icon: {google_icon_path}")
        google_button.setIcon(google_icon)
        google_button.setText("Google")
        google_button.setStyleSheet(
            "background-color: white; color: black; padding: 10px; "
            "border: 1px solid #ccc; border-radius: 5px; text-align: center;"
        )
        google_button.setIconSize(QSize(24, 24))
        social_buttons_layout.addWidget(google_button)

        # Apple Button with centered icon and text, and with border
        apple_button = QPushButton()
        apple_icon_path = r"C:\Users\USUARIO\IdeaProjects\lista_de_tarea\src\Recursos\apple.png"
        apple_icon = QIcon(apple_icon_path)
        if apple_icon.isNull():
            print(f"Error loading apple icon: {apple_icon_path}")
        apple_button.setIcon(apple_icon)
        apple_button.setText("Apple")
        apple_button.setStyleSheet(
            "background-color: white; color: black; padding: 10px; "
            "border: 1px solid #ccc; border-radius: 5px; text-align: center;"
        )
        apple_button.setIconSize(QSize(24, 24))
        social_buttons_layout.addWidget(apple_button)

        right_layout.addLayout(social_buttons_layout)
        right_layout.addStretch(1)

        # --- Add Layouts ---
        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)
        main_layout.setStretch(0, 1)
        main_layout.setStretch(1, 1)

        self.setStyleSheet(
            """
QLineEdit {
padding: 8px;
border: 1px solid #ccc;
border-radius: 4px;
margin-bottom: 8px;
}
            """
        )

    def register_user(self):
        # Obtener datos del formulario
        first_name = self.first_name_input.text().strip()
        last_name = self.last_name_input.text().strip()
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()

        # Validar campos requeridos
        if not all([first_name, last_name, email, password]):
            QMessageBox.warning(self, "Campos incompletos", "❌ Por favor completa todos los campos.")
            return

        if not self.terms_checkbox.isChecked():
            QMessageBox.warning(self, "Términos y Condiciones",
                                "❌ Debes aceptar los Términos & Conditions.")
            return

        # Combinar nombre y apellido en el campo 'name'
        full_name = f"{first_name} {last_name}"

        # Intentar crear el usuario usando la lógica implementada en Usuarios
        nuevo_usuario = Usuarios.create_user(full_name, email, password)
        if nuevo_usuario:
            QMessageBox.information(self, "Registro Exitoso", "✔ Usuario creado, Registro Exitoso.")
            self.main_window = MainWindow(usuario=nuevo_usuario)
            self.main_window.show()
            self.close()
        else:
            QMessageBox.critical(self, "Error en el Registro", "❌ El registro falló.")

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = RegisterWindow()
    window.show()
    sys.exit(app.exec())