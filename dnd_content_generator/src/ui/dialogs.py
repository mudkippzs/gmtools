from PySide6.QtWidgets import QMessageBox

def show_error(parent, message):
    msg = QMessageBox(parent)
    msg.setIcon(QMessageBox.Critical)
    msg.setText(message)
    msg.setWindowTitle("Error")
    msg.exec()

def show_info(parent, message):
    msg = QMessageBox(parent)
    msg.setIcon(QMessageBox.Information)
    msg.setText(message)
    msg.setWindowTitle("Info")
    msg.exec()
