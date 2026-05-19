from PyQt6.QtWidgets import (
    QMessageBox,
    QInputDialog
)

from PyQt6.QtCore import Qt

from modelo.dataframe_model import CSVModel
from modelo.table_dataframe_model import DataFrameModel

from config.config import (
    RUTA_CODIGOS
)


class Controlador_Operadores:

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
            "crear": []
        }

        # ==========================================
        # EVENTOS
        # ==========================================

        self.ui.btn_buscar_op.clicked.connect(
            self.filtrar_operadores
        )

        self.ui.btn_guardar_op.clicked.connect(
            self.guardar_cambios
        )

        self.ui.btn_recargar.clicked.connect(
            self.recargar_datos
        )

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

            self.df = self.modelo.cargar_csv(RUTA_CODIGOS)

            if self.df.empty:

                self.mostrar_error(
                    "Archivo vacío",
                    "El archivo no contiene datos."
                )

                return

            # COPIA ORIGINAL

            self.df_original = self.df.copy()
            self.df = self.df.drop(columns="Cantidad")
            # MODELO TABLA

            self.modelo_tabla = DataFrameModel(self.df)

            # CARGAR TABLA

            self.ui.tb_operadores.setModel(
                self.modelo_tabla
            )

            # AJUSTAR

            self.ui.tb_operadores.resizeColumnsToContents()

            # EVENTO EDICION

            self.modelo_tabla.dataChanged.connect(
                self.registrar_edicion
            )

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

    # ==================================================
    # REGISTRAR EDICION
    # ==================================================

    def registrar_edicion(self):

        try:

            for fila in range(len(self.df)):

                id_operador = str(
                    self.df.iloc[fila, 0]
                )

                self.cambios["editar"][id_operador] = (
                    self.df.iloc[fila].to_dict()
                )

        except Exception as e:

            self.mostrar_error(
                "Error al editar",
                str(e)
            )

    # ==================================================
    # ELIMINAR FILA
    # ==================================================

    def eliminar_fila(self):

        try:

            index = self.ui.tb_operadores.currentIndex()

            if not index.isValid():

                self.mostrar_error(
                    "Selección requerida",
                    "Seleccione una fila."
                )

                return

            fila = index.row()

            id_operador = str(
                self.df.iloc[fila, 0]
            )

            # REGISTRAR ELIMINACION

            self.cambios["eliminar"].append(
                id_operador
            )

            # ELIMINAR

            self.df.drop(
                index=self.df.index[fila],
                inplace=True
            )

            self.df.reset_index(
                drop=True,
                inplace=True
            )

            # ACTUALIZAR TABLA

            self.modelo_tabla._df = self.df
            self.modelo_tabla.layoutChanged.emit()

            self.mostrar_info(
                "Fila eliminada",
                "Registro eliminado correctamente."
            )

        except Exception as e:

            self.mostrar_error(
                "Error al eliminar",
                str(e)
            )

    # ==================================================
    # CREAR FILA
    # ==================================================

    def crear_fila(self):

        try:

            nueva_fila = {}

            # PEDIR DATOS

            for columna in self.df.columns:

                valor, ok = QInputDialog.getText(
                    self.window,
                    "Nuevo registro",
                    f"Ingrese {columna}:"
                )

                if not ok:
                    return

                nueva_fila[columna] = valor

            # AGREGAR

            self.df.loc[len(self.df)] = nueva_fila

            # REGISTRAR

            self.cambios["crear"].append(
                nueva_fila
            )

            # ACTUALIZAR

            self.modelo_tabla._df = self.df
            self.modelo_tabla.layoutChanged.emit()

            self.mostrar_info(
                "Registro creado",
                "Nuevo registro agregado."
            )

        except Exception as e:

            self.mostrar_error(
                "Error al crear",
                str(e)
            )

    # ==================================================
    # GUARDAR CAMBIOS
    # ==================================================

    def guardar_cambios(self):

        try:

            # ==========================================
            # GUARDAR CSV
            # ==========================================

            self.df.to_csv(
                RUTA_CODIGOS,
                index=False
            )

            # ==========================================
            # MOSTRAR CAMBIOS
            # ==========================================

            resumen = (
                f"Editados: "
                f"{len(self.cambios['editar'])}\n"
                f"Creados: "
                f"{len(self.cambios['crear'])}\n"
                f"Eliminados: "
                f"{len(self.cambios['eliminar'])}"
            )

            self.mostrar_info(
                "Cambios guardados",
                resumen
            )

            # LIMPIAR CONTROL

            self.cambios = {
                "editar": {},
                "eliminar": [],
                "crear": []
            }

            # ACTUALIZAR ORIGINAL

            self.df_original = self.df.copy()

        except PermissionError:

            self.mostrar_error(
                "Archivo bloqueado",
                "Cierre el archivo CSV antes de guardar."
            )

        except Exception as e:

            self.mostrar_error(
                "Error al guardar",
                str(e)
            )

    # ==================================================
    # RECARGAR
    # ==================================================

    def recargar_datos(self):

        try:

            self.cargar_tabla_operadores()

            self.mostrar_info(
                "Datos actualizados",
                "La tabla fue recargada."
            )

        except Exception as e:

            self.mostrar_error(
                "Error al recargar",
                str(e)
            )