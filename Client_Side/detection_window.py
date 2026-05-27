from PyQt5.QtWidgets import QMainWindow, QFileDialog, QMessageBox
from PyQt5.uic import loadUi
from PyQt5.QtCore import QThread, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QImage, QPixmap
from detection import Detection
import cv2
import numpy as np

# Manages detection window, starts and stops detection thread
class DetectionWindow(QMainWindow):
    def __init__(self):
        super(DetectionWindow, self).__init__()
        loadUi('UI/detection_window.ui', self)
        
        self.detection = None
        self.stop_detection_button.clicked.connect(self.close)
        
        # Show initial placeholder image
        self.show_placeholder_image()
    
    def show_placeholder_image(self):
        """Show a placeholder image while loading"""
        placeholder = np.zeros((480, 854, 3), dtype=np.uint8)
        placeholder.fill(50)  # Dark gray background
        cv2.putText(placeholder, "Initializing Camera...", (200, 240), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        rgbImage = cv2.cvtColor(placeholder, cv2.COLOR_BGR2RGB)
        convertToQtFormat = QImage(rgbImage.data, 854, 480, 854 * 3, QImage.Format_RGB888)
        p = convertToQtFormat.scaled(854, 480, Qt.KeepAspectRatio)
        self.label_detection.setPixmap(QPixmap.fromImage(p))
    
    @pyqtSlot(QImage)
    def setImage(self, image):
        """Assigns detection output to the label in order to display detection output"""
        if image and not image.isNull():
            self.label_detection.setPixmap(QPixmap.fromImage(image))
    
    def start_detection_camera1(self):
        """Start detection with Camera 1 (DroidCam)"""
        from PyQt5.QtWidgets import QInputDialog
        
        # Ask user for DroidCam IP or use default camera
        ip, ok = QInputDialog.getText(
            self,
            "DroidCam Configuration",
            "Enter DroidCam IP:PORT\n(e.g., 192.168.100.15:4747)\n\nOr leave empty to use default webcam:",
            text=""
        )
        
        if ok:
            if ip.strip():
                # Use DroidCam IP address
                ip_clean = ip.strip()
                # Remove http:// or https:// if present
                if ip_clean.startswith('http://'):
                    ip_clean = ip_clean[7:]
                elif ip_clean.startswith('https://'):
                    ip_clean = ip_clean[8:]
                
                # Remove /video if user accidentally included it
                if ip_clean.endswith('/video'):
                    ip_clean = ip_clean[:-6]
                
                # Check if port is included
                if ':' not in ip_clean:
                    # Default DroidCam port is 4747
                    ip_clean = f"{ip_clean}:4747"
                
                # Format as DroidCam URL (DroidCam uses /video endpoint)
                camera_source = f"http://{ip_clean}/video"
                print(f"Connecting to DroidCam: {camera_source}")
            else:
                # Use default camera index
                camera_source = 0  # Try camera 0 first (usually default webcam)
                print("Using default webcam")
        else:
            # User cancelled, use default camera
            camera_source = 0
            print("Using default webcam (cancelled)")
        
        # Show window first and make sure it stays open
        self.show()
        self.raise_()
        self.activateWindow()
        self.setWindowState(Qt.WindowActive)  # Ensure window is active
        
        # Start detection
        self.detection = Detection(camera_source, self)
        self.detection.changePixmap.connect(self.setImage)
        self.detection.finished.connect(self.on_detection_finished)
        self.detection.start()
    
    def on_detection_finished(self):
        """Called when detection thread finishes"""
        # Check if detection failed
        if self.detection and hasattr(self.detection, 'error_occurred') and self.detection.error_occurred:
            QMessageBox.warning(self, "Camera Error", 
                              "Could not connect to camera.\n\n"
                              "For DroidCam:\n"
                              "1. Make sure DroidCam app is running on your phone\n"
                              "2. Check that phone and laptop are on same WiFi\n"
                              "3. Verify the IP address is correct (e.g., 192.168.1.100:4747)\n\n"
                              "For default camera:\n"
                              "Make sure your webcam is connected and not being used by another application.")
    
    def start_detection_camera2(self):
        """Start detection with Camera 2 (File Upload)"""
        # Open file dialog to select image or video
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Image or Video File",
            "",
            "Image Files (*.jpg *.jpeg *.png *.bmp);;Video Files (*.mp4 *.avi *.mov *.mkv);;All Files (*.*)"
        )
        
        if file_path:
            # Show window first
            self.show()
            self.raise_()
            self.activateWindow()
            self.setWindowState(Qt.WindowActive)  # Ensure window is active
            
            # Start detection
            self.detection = Detection(file_path, self)
            self.detection.changePixmap.connect(self.setImage)
            self.detection.start()
        else:
            QMessageBox.information(self, "No File Selected", "Please select an image or video file.")
    
    def closeEvent(self, event):
        """When closed, stop detection"""
        if self.detection and self.detection.isRunning():
            self.detection.running = False
            self.detection.wait(3000)  # Wait up to 3 seconds for thread to finish
        event.accept()
    
    def showEvent(self, event):
        """Ensure window stays visible when shown"""
        super().showEvent(event)
        self.raise_()
        self.activateWindow()
