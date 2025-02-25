import sys
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QWidget, QMessageBox
from src.logica.usuarios import Usuarios
from src.BaseDatos.Conexion import get_db
from src.vista.Menu.Menu import MainWindow

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        # Cargar la interfaz desde el archivo login.ui
        uic.loadUi("login.ui", self)
        # Crear la sesión de base de datos
        self.db = next(get_db())
        self.user_repository = Usuarios
        self.loginButton.clicked.connect(self.handle_login)
        self.createAccountLabel.linkActivated.connect(self.go_to_register)

    def handle_login(self):
        email = self.emailLineEdit.text().strip()
        password = self.passwordLineEdit.text()
        if not email or not password:
            QMessageBox.warning(self, "Error", "Please fill all fields.")
            return
        # Validar el usuario pasando el email y la contraseña en texto plano.
        # La función validate_user se encarga de verificar la contraseña mediante bcrypt.
        usuario = self.user_repository.validate_user(email, password)
        if usuario:
            QMessageBox.information(self, "Success", "Login successful")
            # Abrir el menú principal y pasarle el usuario autenticado
            self.menu_window = MainWindow(usuario=usuario)
            self.menu_window.show()
            self.close()
        else:
            QMessageBox.warning(self, "Error", "Invalid credentials.")

    def go_to_register(self, link):
        # Aquí se puede agregar la lógica para mostrar la ventana de registro.
        QMessageBox.information(self, "Register", "Registration window should open.")

    def closeEvent(self, event):
        if self.db:
            self.db.close()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())