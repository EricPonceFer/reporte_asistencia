from PyQt6.QtWidgets import QApplication
from controlador.controlador_principal import Controlador
import sys

app = QApplication(sys.argv)

ventana = Controlador()
ventana.show()

sys.exit(app.exec())