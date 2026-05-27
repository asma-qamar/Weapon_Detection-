from PyQt5.QtWidgets import QApplication
import sys
from login_window import LoginWindow

# Starting the application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainwindow = LoginWindow()
    mainwindow.show()
    
    # Exiting
    try:
        sys.exit(app.exec_())
    except: 
        print("Exiting")