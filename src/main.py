from PyQt6.QtWidgets import QApplication
from controlador.main_controller import MainController
import sys

app = QApplication(sys.argv)

ventana = MainController()
ventana.show()

sys.exit(app.exec())