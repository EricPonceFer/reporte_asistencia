from PyQt6.QtWidgets import (
    QFileDialog,
    QMessageBox
)
from modelo.asistencia_model import AsistenciaModel
from PyQt6 import QtCore

class Controlador_Reporte_Asitencia:

    def __init__(self, window, ui):

        # ==========================================
        # RECIBIR UI DEL MAIN
        # ==========================================

        self.ui = ui
        self.window = window

        self.modelo = None

        # Variables
        self.ruta_excel = ""
        self.ruta_guardado = ""

        # ==========================================
        # EVENTOS
        # ==========================================

        self.ui.btn_buscar.clicked.connect(
            self.cargar_excel
        )

        self.ui.btn_guardar.clicked.connect(
            self.seleccionar_carpeta
        )

        self.ui.btn_crear.clicked.connect(
            self.crear_reporte
        )

        self.ui.btn_limpiar.clicked.connect(
            self.limpiar_campos
        )

    # =====================================================
    # CARGAR EXCEL
    # =====================================================

    def cargar_excel(self):

        try:

            ruta, _ = QFileDialog.getOpenFileName(
                self.window,
                "Seleccionar Excel",
                "",
                "Archivos Excel (*.xlsx *.xls)"
            )

            # Usuario canceló
            if not ruta:

                QMessageBox.warning(
                    self.window,
                    "Archivo no seleccionado",
                    "No seleccionó ningún archivo Excel."
                )

                return

            self.ruta_excel = ruta

            self.ui.buscar_archivo.setText(
                ruta
            )

            QMessageBox.information(
                self.window,
                "Archivo cargado",
                "El archivo Excel fue seleccionado correctamente."
            )

        except Exception as error:

            QMessageBox.critical(
                self.window,
                "Error",
                f"Ocurrió un error al cargar el archivo:\\n{error}"
            )

    # =====================================================
    # SELECCIONAR CARPETA
    # =====================================================

    def seleccionar_carpeta(self):

        try:

            ruta = QFileDialog.getExistingDirectory(
                self.window,
                "Seleccionar carpeta"
            )

            # Usuario canceló
            if not ruta:

                QMessageBox.warning(
                    self.window,
                    "Carpeta no seleccionada",
                    "No seleccionó ninguna carpeta."
                )

                return

            self.ruta_guardado = ruta

            self.ui.guardar_archivo.setText(
                ruta
            )
            

        except Exception as error:

            QMessageBox.critical(
                self.window,
                "Error",
                f"Ocurrió un error al seleccionar la carpeta:\\n{error}"
            )
    # =====================================================
    # CREAR REPORTE
    # =====================================================

    def crear_reporte(self):

        try:

            # ==========================================
            # VALIDAR ARCHIVO
            # ==========================================

            if not self.ui.buscar_archivo.text().strip():

                QMessageBox.warning(
                    self.window,
                    "Archivo faltante",
                    "Debe seleccionar un archivo Excel."
                )

                return

            # ==========================================
            # VALIDAR CARPETA
            # ==========================================

            if not self.ui.guardar_archivo.text().strip():

                QMessageBox.warning(
                    self.window,
                    "Carpeta faltante",
                    "Debe seleccionar una carpeta de guardado."
                )

                return

            # ==========================================
            # VALIDAR NOMBRE ARCHIVO
            # ==========================================

            nombre_archivo = (
                self.ui.nombre_archivo.text().strip()
            )

            if not nombre_archivo:

                QMessageBox.warning(
                    self.window,
                    "Nombre faltante",
                    "Debe ingresar un nombre para el archivo."
                )

                return

            # ==========================================
            # VALIDAR FECHAS
            # ==========================================

            fecha_inicio = (
                self.ui.dt_comienzo.date().toPyDate()
            )

            fecha_final = (
                self.ui.dt_final.date().toPyDate()
            )

            # Fecha inicio mayor
            if fecha_inicio > fecha_final:

                QMessageBox.warning(
                    self.window,
                    "Fechas inválidas",
                    "La fecha de inicio no puede ser mayor a la fecha final."
                )

                return

            # Validar año 2026
            if fecha_inicio.year < 2026:

                QMessageBox.warning(
                    self.window,
                    "Fecha inválida",
                    "La fecha de inicio debe ser mayor o igual al año 2026."
                )

                return

            if fecha_final.year < 2026:

                QMessageBox.warning(
                    self.window,
                    "Fecha inválida",
                    "La fecha final debe ser mayor al año 2025."
                )

                return

            # ==========================================
            # RUTA FINAL
            # ==========================================

            nombre_archivo = (
                f"{nombre_archivo}.xlsx"
            )

            # ruta_final = (
            #     Path(self.ruta_guardado)
            #     / nombre_archivo
            # )

            # ==========================================
            # PROCESAMIENTO
            # ==========================================

            modelo = AsistenciaModel(
                ruta_asistencia=self.ruta_excel,
                ruta_guardado=self.ruta_guardado
            )
            modelo.cargar_archivos()


            dataframe_resultado = (
                modelo.procesar_asistencia()
            )

            modelo.exportar_excel(
                dataframe_resultado,
                nombre_archivo
            )
            # ==========================================
            # MENSAJE FINAL
            # ==========================================

            QMessageBox.information(
                self.window,
                "Proceso completado",
                "El reporte fue generado correctamente."
            )

        except Exception as error:

            QMessageBox.critical(
                self.window,
                "Error",
                f"Ocurrió un error durante el proceso:\\n{error}"
            )
    
    # ==========================================
    # LIMPIAR TEXTOS
    # ==========================================
    def limpiar_campos(self):

        try:
            self.ui.buscar_archivo.clear()
            self.ui.guardar_archivo.clear()
            self.ui.nombre_archivo.clear()

            # ==========================================
            # LIMPIAR VARIABLES
            # ==========================================
            self.ruta_excel = ""
            self.ruta_guardado = ""

            # ==========================================
            # RESTABLECER FECHAS
            # ==========================================
            fecha_minima = QtCore.QDate(2026, 1, 1)
            fecha_maxima = QtCore.QDate(2026, 12, 31)

            # Limitar fechas
            self.ui.dt_comienzo.setMinimumDate(
                fecha_minima
            )

            self.ui.dt_comienzo.setMaximumDate(
                fecha_maxima
            )

            self.ui.dt_final.setMinimumDate(
                fecha_minima
            )

            self.ui.dt_final.setMaximumDate(
                fecha_maxima
            )

            # Fecha actual
            hoy = QtCore.QDate.currentDate()
            self.ui.dt_comienzo.setDate(fecha_minima)
            self.ui.dt_final.setDate(hoy)

            # ==========================================
            # MENSAJE
            # ==========================================

            QMessageBox.information(
                self.window,
                "Campos limpiados",
                "Todos los campos fueron restablecidos correctamente."
            )

        except Exception as error:

            QMessageBox.critical(
                self.window,
                "Error",
                f"Ocurrió un error al limpiar los campos:\\n{error}"
            )