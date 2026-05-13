from vista.interfaz_reporte import Ui_MainWindow
# from modelo.procesador_excel import ProcesadorExcel

from PyQt6.QtWidgets import QMainWindow, QFileDialog

class Controlador(QMainWindow):

    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # self.boton_cargar.clicked.connect(self.cargar_excel)

    def cargar_excel(self):

        ruta, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar Excel",
            "",
            "Excel (*.xlsx)"
        )

        if ruta:

            df = self.modelo.procesar_archivo(ruta)

            df.to_excel("salida/reporte.xlsx", index=False)

            self.label_estado.setText("Archivo procesado")