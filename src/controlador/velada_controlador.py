from PyQt6.QtWidgets import (
    QMessageBox,
    QInputDialog
)

from PyQt6.QtCore import Qt

from modelo.dataframe_model import CSVModel
from modelo.table_dataframe_model import DataFrameModel

from config.config import (
    RUTA_VELADA
)


class Controlador_Velada:

    def __init__(self, window, ui):

        # ==========================================
        # RECIBIR UI
        # ==========================================

        self.ui = ui
        self.window = window

        # ==========================================
        # MODELOS
        # ==========================================

        self.modelo = CSVModel()

        self.df = None
        self.df_original = None

        self.modelo_tabla = None

        # ==========================================
        # CONTROL DE CAMBIOS
        # ==========================================

        self.cambios = {
            "editar": {},
            "eliminar": [],
            "crear": []
        }

        # ==========================================
        # EVENTOS
        # ==========================================

        self.ui.btn_buscar_vl.clicked.connect(
            self.filtrar_operadores
        )

        # self.ui.btn_guardar_vl.clicked.connect(
        #     self.guardar_cambios
        # )

        # self.ui.btn_eliminar.clicked.connect(
        #     self.recargar_datos
        # )

        # ==========================================
        # CARGAR TABLA
        # ==========================================

        self.cargar_tabla_operadores()

    # ==================================================
    # MENSAJES
    # ==================================================

    def mostrar_error(self, titulo, mensaje):

        QMessageBox.critical(
            self.window,
            titulo,
            mensaje
        )

    def mostrar_info(self, titulo, mensaje):

        QMessageBox.information(
            self.window,
            titulo,
            mensaje
        )

    # ==================================================
    # CARGAR TABLA
    # ==================================================

    def cargar_tabla_operadores(self):

        try:

            self.df = self.modelo.cargar_csv(RUTA_VELADA)

            if self.df.empty:

                self.mostrar_error(
                    "Archivo vacío",
                    "El archivo no contiene datos."
                )

                return

            # COPIA ORIGINAL

            self.df_original = self.df.copy()

            # MODELO TABLA

            self.modelo_tabla = DataFrameModel(self.df)

            # CARGAR TABLA

            self.ui.tb_velada.setModel(
                self.modelo_tabla
            )

            # AJUSTAR

            self.ui.tb_velada.resizeColumnsToContents()

            # EVENTO EDICION



        except Exception as e:

            self.mostrar_error(
                "Error",
                str(e)
            )

    # ==================================================
    # FILTRAR
    # ==================================================

    def filtrar_operadores(self):

        try:

            texto = (
                self.ui.buscar_archivo_2.text()
                .strip()
                .lower()
            )

            # ==========================================
            # SIN TEXTO
            # ==========================================

            if not texto:

                self.df = self.df_original.copy()

            else:

                # ==========================================
                # FILTRAR SOLO POR:
                # CODIGO Y NOMBRES
                # ==========================================

                filtro = (

                    self.df_original["CODIGO"]
                    .astype(str)
                    .str.lower()
                    .str.contains(texto, na=False)

                ) | (

                    self.df_original["NOMBRES"]
                    .astype(str)
                    .str.lower()
                    .str.contains(texto, na=False)

                )

                self.df = self.df_original[
                    filtro
                ].copy()

            # ==========================================
            # RECARGAR TABLA
            # ==========================================

            self.modelo_tabla._df = self.df
            self.modelo_tabla.layoutChanged.emit()

        except KeyError as e:

            self.mostrar_error(
                "Columna no encontrada",
                f"No existe la columna:\n{str(e)}"
            )

        except Exception as e:

            self.mostrar_error(
                "Error al buscar",
                str(e)
            )