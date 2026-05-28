from PyQt6.QtWidgets import (QMessageBox, QInputDialog, QMenu)
import pandas as pd
from PyQt6.QtCore import Qt
from vista.ventana_modificacion import VentanaModificar
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
            "crear": [],
            "eliminar": [],
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

        # self.ui.btn_crear_op.clicked.connect(
        #     self.crear_fila
        # )

        # ==========================================
        # CARGAR TABLA
        # ==========================================

        self.cargar_tabla_operadores()
        self.ui.tb_operadores.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu
        )

        self.ui.tb_operadores.customContextMenuRequested.connect(
            self.menu_operadores
        )
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
            # FILTRO BASE
            # ==========================================

            filtro = pd.Series(
                True,
                index=self.df_original.index
            )

            # ==========================================
            # FILTRO POR TEXTO
            # ==========================================

            if texto:

                filtro_texto = (

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

                filtro &= filtro_texto

            # ==========================================
            # FILTRO POR ACTIVO
            # ==========================================

            if self.ui.rb_Disponibles.isChecked():

                filtro_activo = (

                    self.df_original["ACTIVO"]
                    .astype(str)
                    .str.upper()
                    == "SI"
                )

                filtro &= filtro_activo

            elif self.ui.rb_NDisponibles.isChecked():

                filtro_activo = (

                    self.df_original["ACTIVO"]
                    .astype(str)
                    .str.upper()
                    == "NO"
                )

                filtro &= filtro_activo

            # ==========================================
            # FILTRAR DATAFRAME
            # ==========================================

            self.df = self.df_original[
                filtro
            ].copy()

            # ==========================================
            # RECARGAR TABLA
            # ==========================================

            self.modelo_tabla._df = self.df
            self.modelo_tabla.layoutChanged.emit()
            self.ui.tb_operadores.resizeColumnsToContents()

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
    # MENU CONCEPTUAL
    # ==================================================

    def menu_operadores(self, posicion):

        try:

            index = self.ui.tb_operadores.indexAt(
                posicion
            )

            if not index.isValid():
                return

            indice_real = self.df.index[
                index.row()
            ]

            menu = QMenu()

            accion_modificar = menu.addAction(
                "Modificar"
            )

            # accion_eliminar = menu.addAction(
            #     "Eliminar"
            # )

            accion = menu.exec(
                self.ui.tb_operadores
                .viewport()
                .mapToGlobal(posicion)
            )

            # ==========================================
            # MODIFICAR
            # ==========================================

            if accion == accion_modificar:

                self.modificar_fila(
                    indice_real
                )

            # ==========================================
            # ELIMINAR
            # ==========================================

            # elif accion == accion_eliminar:

            #     self.eliminar_fila(
            #         indice_real
            #     )

        except Exception as e:

            self.mostrar_error(
                "Error",
                f"Error en realizar la acción:\n{e}"
            )

    def modificar_fila(self, fila):

        try:

            datos = self.df.iloc[fila]

            ventana = VentanaModificar(
                datos,
                self.window
            )

            if ventana.exec():

                columna = ventana.columna
                nuevo_valor = ventana.valor


                valor_original = self.df_original.at[
                    fila,
                    columna
                ]

                tipo_original = type(
                    valor_original
                )

                nuevo_valor = tipo_original(
                    nuevo_valor
                )


                if fila not in self.cambios["editar"]:

                    self.cambios["editar"][fila] = {}


                self.cambios["editar"][fila][
                    columna
                ] = nuevo_valor

                self.df.at[
                    fila,
                    columna
                ] = nuevo_valor

                self.modelo_tabla._df = self.df

                self.modelo_tabla.layoutChanged.emit()

                self.mostrar_info(
                    "Registro actualizado",
                    "Campo modificado correctamente."
                )

        except ValueError:

            self.mostrar_error(
                "Dato inválido",
                "El tipo de dato ingresado no es válido."
            )

        except Exception as e:

            self.mostrar_error(
                "Error al modificar",
                f"Ocurrió un error:\n{e}"
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

    def eliminar_fila(self, fila):

        try:

            respuesta = QMessageBox.question(
                self.window,
                "Confirmar eliminación",
                "¿Desea eliminar el registro?",
                QMessageBox.StandardButton.Yes |
                QMessageBox.StandardButton.No
            )

            if respuesta != QMessageBox.StandardButton.Yes:
                return

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
                f"No se Logro Eliminar el Registro  {e}"
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

            # REGISTRAR EN CAMBIOS

            self.cambios["crear"].append(
                nueva_fila
            )

            # AGREGAR A DATAFRAME TEMPORAL

            self.df = pd.concat(
                [
                    self.df,
                    pd.DataFrame([nueva_fila])
                ],
                ignore_index=True
            )

            # ACTUALIZAR TABLA

            self.modelo_tabla._df = self.df
            self.modelo_tabla.layoutChanged.emit()
            self.ui.tb_operadores.resizeColumnsToContents()

            self.mostrar_info(
                "Registro creado",
                "Nuevo registro agregado. Guarde para confirmar."
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

            df_actualizado = self.df_original.copy()

            if self.cambios["eliminar"]:
                df_actualizado = df_actualizado.drop(
                    self.cambios["eliminar"]
                )

            for fila, cambios_fila in self.cambios["editar"].items():

                for columna, nuevo_valor in cambios_fila.items():

                    df_actualizado.at[
                        fila,
                        columna
                    ] = nuevo_valor

            if self.cambios["crear"]:

                df_nuevas = pd.DataFrame(
                    self.cambios["crear"]
                )

                df_actualizado = pd.concat(
                    [
                        df_actualizado,
                        df_nuevas
                    ],
                    ignore_index=True
                )

            df_actualizado = df_actualizado.reset_index(drop=True)

            df_actualizado.to_csv(
                RUTA_CODIGOS,
                index=False
            )

            self.df = df_actualizado.copy()
            self.df_original = df_actualizado.copy()

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

            self.cambios = {
                "editar": {},
                "crear": [],
                "eliminar": []
            }

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
            self.df = self.df_original.copy()

            self.cambios = {
                "editar": {},
                "crear": [],
                "eliminar": []
            }

            self.modelo_tabla._df = self.df

            self.modelo_tabla.layoutChanged.emit()

            self.mostrar_info(
                "Datos actualizados",
                "La tabla fue recargada."
            )

        except Exception as e:

            self.mostrar_error(
                "Error al recargar",
                str(e)
            )