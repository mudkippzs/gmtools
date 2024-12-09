import sys
from PySide6.QtWidgets import QApplication
from src.controllers.app_controller import AppController
from src.ui.main_window import MainWindow

def main():
    app_controller = AppController()
    app = QApplication(sys.argv)
    window = MainWindow(app_controller)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
