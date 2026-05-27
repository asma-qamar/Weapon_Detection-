from PyQt5.QtWidgets import QMainWindow, QMenu, QAction
from PyQt5.QtCore import Qt
from PyQt5.uic import loadUi

# MainWindow class that manages the main menu
class MainWindow(QMainWindow):
    def __init__(self, user_data):
        super(MainWindow, self).__init__()
        loadUi('UI/main_window.ui', self)
        
        self.user_data = user_data
        
        # Create menu for cameras button
        self.create_camera_menu()
        
        self.logout_button.clicked.connect(self.logout)
    
    def create_camera_menu(self):
        """Create dropdown menu for cameras button"""
        camera_menu = QMenu(self)
        
        # Camera 1 Action (Phone/DroidCam)
        camera1_action = QAction("Camera 1 (Phone/Webcam)", self)
        camera1_action.triggered.connect(self.open_camera1)
        camera_menu.addAction(camera1_action)
        
        # Camera 2 Action (File Upload)
        camera2_action = QAction("Camera 2 (Video/Image File)", self)
        camera2_action.triggered.connect(self.open_camera2)
        camera_menu.addAction(camera2_action)
        
        # Set menu to button
        self.cameras_button.setMenu(camera_menu)
    
    def open_camera1(self):
        """Open Camera 1 (DroidCam)"""
        from detection_window import DetectionWindow
        detection_window = DetectionWindow()
        detection_window.start_detection_camera1()
        self.hide()
    
    def open_camera2(self):
        """Open Camera 2 (File Upload)"""
        from detection_window import DetectionWindow
        detection_window = DetectionWindow()
        detection_window.start_detection_camera2()
        self.hide()
    
    def logout(self):
        """Logout and return to login window"""
        from login_window import LoginWindow
        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()

