import sys
import os
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QCheckBox,
    QMessageBox
)
from PyQt6.QtGui import QFont, QIcon, QPixmap
from PyQt6.QtCore import Qt, QSize
from src.logica.usuarios import Usuarios
from src.vista.Menu.Menu import MainWindow

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Log In")
        self.setup_ui()

    def setup_ui(self):
        main_layout = QHBoxLayout(self)

        # --- Left Side (Image) ---
        left_layout = QVBoxLayout()

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

        # --- Right Side (Login Form) ---
        right_layout = QVBoxLayout()

        # --- Top Bar (Logo) ---
        top_bar_layout = QHBoxLayout()
        logo_label = QLabel("LISTA-TAREAS")
        logo_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        top_bar_layout.addWidget(logo_label)
        top_bar_layout.addStretch()
        right_layout.addLayout(top_bar_layout)

        # --- Page Title ---
        title_label = QLabel("Log In")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        right_layout.addWidget(title_label)

        # --- Email Field ---
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")
        email_icon_path = r"C:\Users\USUARIO\IdeaProjects\lista_de_tarea\src\Recursos\icons8-email-24.png"
        email_icon = QIcon(email_icon_path)
        if not email_icon.isNull():
            self.email_input.addAction(email_icon, QLineEdit.ActionPosition.LeadingPosition)
        else:
            print(f"Error: Could not load email icon from {email_icon_path}")
        right_layout.addWidget(self.email_input)

        # --- Password Field ---
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        password_icon_path = r"C:\Users\USUARIO\IdeaProjects\lista_de_tarea\src\Recursos\icons8-password-24.png"
        password_icon = QIcon(password_icon_path)
        if not password_icon.isNull():
            self.password_input.addAction(password_icon, QLineEdit.ActionPosition.LeadingPosition)
        else:
            print(f"Error: Could not load password icon from {password_icon_path}")
        right_layout.addWidget(self.password_input)

        # --- Remember Me Checkbox ---
        self.remember_checkbox = QCheckBox("Remember me")
        right_layout.addWidget(self.remember_checkbox)

        # --- Login Button ---
        self.login_button = QPushButton("Log In")
        self.login_button.setStyleSheet(
            "background-color: #800080; color: white; padding: 10px; border-radius: 5px;"
        )
        self.login_button.clicked.connect(self.handle_login)
        right_layout.addWidget(self.login_button)

        # --- Or Log In With (Social Buttons) ---
        or_label = QLabel("Or log in with")
        or_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(or_label)

        social_buttons_layout = QHBoxLayout()

        # Google Button
        google_button = QPushButton("Google")
        google_icon_path = r"C:\Users\USUARIO\IdeaProjects\lista_de_tarea\src\Recursos\google.png"
        google_icon = QIcon(google_icon_path)
        if google_icon.isNull():
            print(f"Error loading google icon: {google_icon_path}")
        google_button.setIcon(google_icon)
        google_button.setIconSize(QSize(24, 24))
        google_button.setStyleSheet(
            "background-color: white; color: black; padding: 10px; "
            "border: 1px solid #ccc; border-radius: 5px;"
        )
        social_buttons_layout.addWidget(google_button)

        # Apple Button
        apple_button = QPushButton("Apple")
        apple_icon_path = r"C:\Users\USUARIO\IdeaProjects\lista_de_tarea\src\Recursos\apple.png"
        apple_icon = QIcon(apple_icon_path)
        if apple_icon.isNull():
            print(f"Error loading apple icon: {apple_icon_path}")
        apple_button.setIcon(apple_icon)
        apple_button.setIconSize(QSize(24, 24))
        apple_button.setStyleSheet(
            "background-color: white; color: black; padding: 10px; "
            "border: 1px solid #ccc; border-radius: 5px;"
        )
        social_buttons_layout.addWidget(apple_button)

        # --- GitHub Button ---
        github_button = QPushButton("GitHub")
        github_icon_path = r"C:\Users\USUARIO\IdeaProjects\lista_de_tarea\src\Recursos\github.png"
        github_icon = QIcon(github_icon_path)
        if github_icon.isNull():
            print(f"Error loading github icon: {github_icon_path}")
        github_button.setIcon(github_icon)
        github_button.setIconSize(QSize(24, 24))
        github_button.setStyleSheet(
            "background-color: white; color: black; padding: 10px; "
            "border: 1px solid #ccc; border-radius: 5px;"
        )
        social_buttons_layout.addWidget(github_button)

        right_layout.addLayout(social_buttons_layout)
        right_layout.addStretch(1)

        # --- Assemble Layouts ---
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

    def handle_login(self):
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()

        if not email or not password:
            QMessageBox.warning(self, "Error", "Please fill all fields.")
            return

        usuario = Usuarios.validate_user(email, password)
        if usuario:
            QMessageBox.information(self, "Success", "Login successful")
            self.main_window = MainWindow(usuario=usuario)
            self.main_window.show()
            self.close()
        else:
            QMessageBox.warning(self, "Error", "Invalid credentials.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())