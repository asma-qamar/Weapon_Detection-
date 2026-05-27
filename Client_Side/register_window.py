from PyQt5.QtWidgets import QMainWindow, QMessageBox
from PyQt5.uic import loadUi
from user_storage import register_user

# RegisterWindow class that manages user registration
class RegisterWindow(QMainWindow):
    def __init__(self, login_window):
        super(RegisterWindow, self).__init__()
        loadUi('UI/register_window.ui', self)
        
        self.login_window = login_window
        
        self.register_button.clicked.connect(self.register)
        self.back_button.clicked.connect(self.go_back)
        
        self.popup = QMessageBox()
        self.popup.setWindowTitle("Registration")
    
    def register(self):
        """Handle user registration"""
        firstname = self.firstname_input.text().strip()
        lastname = self.lastname_input.text().strip()
        password = self.password_input.text()
        
        # Validate inputs
        if not firstname or not lastname or not password:
            self.popup.setText("All fields are required!")
            self.popup.setIcon(QMessageBox.Warning)
            self.popup.exec_()
            return
        
        if len(password) < 4:
            self.popup.setText("Password must be at least 4 characters long!")
            self.popup.setIcon(QMessageBox.Warning)
            self.popup.exec_()
            return
        
        # Register user
        success, message = register_user(firstname, lastname, password)
        
        if success:
            self.popup.setText(f"Registration successful!\nYour username is: {message}\nYou can now login.")
            self.popup.setIcon(QMessageBox.Information)
            self.popup.exec_()
            self.go_back()
        else:
            self.popup.setText(message)
            self.popup.setIcon(QMessageBox.Warning)
            self.popup.exec_()
    
    def go_back(self):
        """Return to login window"""
        self.close()
        self.login_window.show()

