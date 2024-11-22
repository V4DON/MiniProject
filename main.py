from PySide6.QtWidgets import QApplication
from main_window import MainWindow

app = QApplication([])
window = MainWindow()
if window.is_logged_in:
    window.show()


app.exec()