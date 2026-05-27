from PyQt5.QtWidgets import QMainWindow, QMessageBox, QDialog, QLineEdit, QPushButton, QLabel, QVBoxLayout
from PyQt5.uic import loadUi
from user_storage import login_user
from main_window import MainWindow

# LoginWindow class that manages login
class LoginWindow(QMainWindow):
    def __init__(self):
        super(LoginWindow, self).__init__()
        loadUi('UI/login_window.ui', self)
        
        self.login_button.clicked.connect(self.show_login_dialog)
        self.register_button.clicked.connect(self.go_to_register)
        
        self.popup = QMessageBox()
        self.popup.setWindowTitle("Login")
        
        self.main_window = None
    
    def show_login_dialog(self):
        """Show login dialog with username and password fields"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Login")
        dialog.setModal(True)
        dialog.resize(350, 200)
        
        layout = QVBoxLayout()
        
        label_title = QLabel("Enter Login Credentials")
        label_title.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(label_title)
        
        label_username = QLabel("Username:")
        layout.addWidget(label_username)
        
        username_input = QLineEdit()
        username_input.setPlaceholderText("Enter username (e.g., firstname_lastname)")
        layout.addWidget(username_input)
        
        label_password = QLabel("Password:")
        layout.addWidget(label_password)
        
        password_input = QLineEdit()
        password_input.setEchoMode(QLineEdit.Password)
        password_input.setPlaceholderText("Enter password")
        layout.addWidget(password_input)
        
        login_btn = QPushButton("Login")
        login_btn.clicked.connect(lambda: self.login(username_input.text(), password_input.text(), dialog))
        layout.addWidget(login_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.close)
        layout.addWidget(cancel_btn)
        
        dialog.setLayout(layout)
        dialog.exec_()
    
    def login(self, username, password, dialog):
        """Handle user login"""
        if not username or not password:
            self.popup.setText("Please enter both username and password!")
            self.popup.setIcon(QMessageBox.Warning)
            self.popup.exec_()
            return
        
        success, message = login_user(username, password)
        
        if success:
            dialog.close()
            self.open_main_window(message)
        else:
            self.popup.setText(message)
            self.popup.setIcon(QMessageBox.Warning)
            self.popup.exec_()
    
    def go_to_register(self):
        """Open registration window"""
        from register_window import RegisterWindow
        self.register_window = RegisterWindow(self)
        self.register_window.show()
        self.hide()
    
    def open_main_window(self, user_data):
        """Open main window after successful login"""
        self.main_window = MainWindow(user_data)
        self.main_window.show()
        self.hide()
