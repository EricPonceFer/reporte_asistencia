from PyQt6.QtWidgets import (
    QMessageBox,
    QInputDialog,
    QMenu
)

from PyQt6.QtCore import Qt
from datetime import datetime
import pandas as pd

from modelo.dataframe_model import CSVModel
from modelo.table_dataframe_model import DataFrameModel
from vista.ventana_modificacion import VentanaModificar

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
        # MAPEO DE INDICES
        # ==========================================
        
        self.indice_mapa = {}  # Mapea posición visual -> índice original

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

        self.ui.btn_guardar_vl.clicked.connect(
            self.guardar_cambios
        )

        self.ui.btn_eliminar.clicked.connect(
            self.recargar_datos
        )

        # ==========================================
        # CARGAR TABLA
        # ==========================================

        self.cargar_tabla_operadores()
        self.ui.tb_velada.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu
        )

        self.ui.tb_velada.customContextMenuRequested.connect(
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

            self.df = self.modelo.cargar_csv(RUTA_VELADA)

            if self.df.empty:

                self.mostrar_error(
                    "Archivo vacío",
                    "El archivo no contiene datos."
                )

                return

            # COPIA ORIGINAL

            self.df_original = self.df.copy()
            
            # ==========================================
            # ORDENAR POR FECHA_INICIO (MAS NUEVO A MAS VIEJO)
            # ==========================================
            
            if "Fecha Inicio" in self.df_original.columns:
                self.df_original = self.df_original.sort_values(
                    by="Fecha Inicio",
                    ascending=False
                ).reset_index(drop=True)
            
            # COPIAR PARA LA TABLA
            
            self.df = self.df_original.copy()
            
            # INICIALIZAR MAPEO DE INDICES
            
            self._actualizar_mapeo_indices()

            # MODELO TABLA

            self.modelo_tabla = DataFrameModel(self.df)

            # CARGAR TABLA

            self.ui.tb_velada.setModel(
                self.modelo_tabla
            )

            # AJUSTAR

            self.ui.tb_velada.resizeColumnsToContents()

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
    # ACTUALIZAR MAPEO DE INDICES
    # ==================================================

    def _actualizar_mapeo_indices(self):
        """
        Crea un mapeo entre posiciones visuales (0, 1, 2...)
        e índices originales del dataframe.
        """
        self.indice_mapa = {}
        for posicion, indice_original in enumerate(self.df.index):
            self.indice_mapa[posicion] = indice_original

    # ==================================================
    # FILTRAR
    # ==================================================

    def filtrar_operadores(self):

        try:

            # ==========================================
            # OBTENER FECHAS
            # ==========================================

            fecha_desde = self.ui.dt_velada_fecha.date().toPyDate()
            fecha_hasta = datetime.now().date()

            # ==========================================
            # OBTENER TEXTO DE BUSQUEDA
            # ==========================================

            texto_busqueda = self.ui.buscar_archivo_vl.text().strip().lower()

            # ==========================================
            # VALIDAR COLUMNA FECHA
            # ==========================================

            if "Fecha Inicio" not in self.df_original.columns:
                self.mostrar_error(
                    "Error",
                    "No se encontró la columna 'Fecha Inicio' en los datos."
                )
                return

            # ==========================================
            # CONVERTIR FECHAS
            # ==========================================

            fecha_temp = pd.to_datetime(
                self.df_original["Fecha Inicio"],
                errors='coerce'
            )

            # ==========================================
            # FILTRO POR FECHA
            # ==========================================

            filtro_fecha = (
                (fecha_temp.dt.date >= fecha_desde) &
                (fecha_temp.dt.date <= fecha_hasta)
            )

            df_filtrado = self.df_original[filtro_fecha].copy()

            # ==========================================
            # FILTRO POR TEXTO (CODIGO O NOMBRE)
            # ==========================================

            if texto_busqueda:
                mask = False
                for col in ["CODIGO", "NOMBRES"]:
                    mask = mask | df_filtrado[col].astype(str).str.lower().str.contains(texto_busqueda)

                df_filtrado = df_filtrado[mask]

            # ==========================================
            # ORDENAR
            # ==========================================

            self.df = df_filtrado.sort_values(
                by="Fecha Inicio",
                ascending=False
            ).copy()

            self.df.reset_index(drop=True, inplace=True)

            self._actualizar_mapeo_indices()

            # ==========================================
            # ACTUALIZAR TABLA
            # ==========================================

            self.modelo_tabla._df = self.df
            self.modelo_tabla.layoutChanged.emit()
            self.ui.tb_velada.resizeColumnsToContents()


        except Exception as e:

            self.mostrar_error(
                "Error al filtrar",
                str(e)
            )
    # ==================================================
    # MENU CONTEXTUAL
    # ==================================================

    def menu_operadores(self, posicion):

        try:

            index = self.ui.tb_velada.indexAt(
                posicion
            )

            if not index.isValid():
                return

            # OBTENER INDICE ORIGINAL USANDO MAPEO
            
            posicion_visual = index.row()
            indice_real = self.indice_mapa.get(
                posicion_visual,
                self.df_original.index[posicion_visual]
            )

            menu = QMenu()

            accion_modificar = menu.addAction(
                "Modificar"
            )

            accion_eliminar = menu.addAction(
                "Eliminar"
            )

            accion = menu.exec(
                self.ui.tb_velada
                .viewport()
                .mapToGlobal(posicion)
            )

            # ==========================================
            # MODIFICAR
            # ==========================================

            if accion == accion_modificar:

                self.modificar_fila(
                    posicion_visual,
                    indice_real
                )

            # ==========================================
            # ELIMINAR
            # ==========================================

            elif accion == accion_eliminar:

                self.eliminar_fila(
                    posicion_visual,
                    indice_real
                )

        except Exception as e:

            self.mostrar_error(
                "Error",
                f"Error en realizar la acción:\n{e}"
            )

    def modificar_fila(self, posicion_visual, indice_original):

        try:

            datos = self.df.iloc[posicion_visual]

            ventana = VentanaModificar(
                datos,
                self.window
            )

            if ventana.exec():

                columna = ventana.columna
                nuevo_valor = ventana.valor

                valor_original = self.df_original.at[
                    indice_original,
                    columna
                ]

                tipo_original = type(
                    valor_original
                )

                # ==========================================
                # VALIDAR SEGUN TIPO DE DATO
                # ==========================================

                nuevo_valor = self._validar_tipo_dato(
                    nuevo_valor,
                    tipo_original,
                    columna
                )

                if nuevo_valor is None:
                    return

                if indice_original not in self.cambios["editar"]:

                    self.cambios["editar"][indice_original] = {}

                self.cambios["editar"][indice_original][
                    columna
                ] = nuevo_valor

                self.df.at[
                    posicion_visual,
                    columna
                ] = nuevo_valor

                self.modelo_tabla._df = self.df

                self.modelo_tabla.layoutChanged.emit()

                self.mostrar_info(
                    "Registro actualizado",
                    "Campo modificado correctamente."
                )

        except Exception as e:

            self.mostrar_error(
                "Error al modificar",
                f"Ocurrió un error:\n{e}"
            )

    # ==================================================
    # VALIDAR TIPO DE DATO
    # ==================================================

    def _validar_tipo_dato(self, valor, tipo_esperado, nombre_columna):

        # ==========================================
        # FECHAS (datetime64)
        # ==========================================
        if pd.api.types.is_datetime64_any_dtype(tipo_esperado):
            nuevo_valor = self._validar_y_convertir_fecha(valor, nombre_columna)
            return nuevo_valor

        # ==========================================
        # ENTEROS (int64)
        # ==========================================
        elif pd.api.types.is_integer_dtype(tipo_esperado):
            try:
                return int(valor)
            except ValueError:
                self.mostrar_error(
                    "Dato inválido",
                    f"El campo '{nombre_columna}' requiere un número entero."
                )
                return None

        # ==========================================
        # DECIMALES (float64)
        # ==========================================
        elif pd.api.types.is_float_dtype(tipo_esperado):
            try:
                return float(valor)
            except ValueError:
                self.mostrar_error(
                    "Dato inválido",
                    f"El campo '{nombre_columna}' requiere un número decimal."
                )
                return None

        # ==========================================
        # BOOLEANOS
        # ==========================================
        elif pd.api.types.is_bool_dtype(tipo_esperado):
            valor_lower = str(valor).lower().strip()

            if valor_lower in ("si", "true", "1", "v", "verdadero"):
                return True
            elif valor_lower in ("no", "false", "0", "f", "falso"):
                return False
            else:
                self.mostrar_error(
                    "Dato inválido",
                    f"El campo '{nombre_columna}' requiere un valor booleano (SI/NO)."
                )
                return None

        # ==========================================
        # TEXTO (object)
        # ==========================================
        else:
            return str(valor)

    # ==================================================
    # VALIDAR TIPO FECHA
    # ==================================================

    def _es_tipo_fecha(self, tipo):
        """
        Verifica si el tipo es de fecha
        """
        return tipo in (
            datetime,
            type(pd.Timestamp("2020-01-01")),
            type(pd.NaT)
        ) or "datetime" in str(tipo).lower()

    # ==================================================
    # VALIDAR Y CONVERTIR FECHA
    # ==================================================

    def _validar_y_convertir_fecha(self, valor_str, nombre_columna):
        """
        Valida y convierte una cadena a fecha con múltiples formatos
        """
        formatos = [
            "%d/%m/%Y",      # 25/12/2023
            "%Y-%m-%d",      # 2023-12-25
            "%d-%m-%Y",      # 25-12-2023
            "%m/%d/%Y",      # 12/25/2023
            "%Y/%m/%d",      # 2023/12/25
            "%d.%m.%Y",      # 25.12.2023
            "%d %m %Y",      # 25 12 2023
            "%Y%m%d",        # 20231225
        ]

        for formato in formatos:

            try:
                fecha_obj = datetime.strptime(
                    valor_str.strip(),
                    formato
                )

                return fecha_obj

            except ValueError:
                continue

        # ==========================================
        # SI NO COINCIDE CON NINGUN FORMATO
        # ==========================================

        self.mostrar_error(
            "Fecha inválida",
            f"El campo '{nombre_columna}' requiere una fecha válida.\n\n"
            f"No se pueden ingresar letras sin formato de fecha.\n\n"
            f"Formatos aceptados:\n"
            f"• DD/MM/YYYY (25/12/2023)\n"
            f"• YYYY-MM-DD (2023-12-25)\n"
            f"• DD-MM-YYYY (25-12-2023)\n"
            f"• MM/DD/YYYY (12/25/2023)\n"
            f"• YYYY/MM/DD (2023/12/25)\n"
            f"• DD.MM.YYYY (25.12.2023)"
        )

        return None

    # ==================================================
    # REGISTRAR EDICION
    # ==================================================

    def registrar_edicion(self):

        try:

            for posicion in range(len(self.df)):

                indice_original = self.indice_mapa.get(
                    posicion,
                    self.df_original.index[posicion]
                )

                self.cambios["editar"][indice_original] = (
                    self.df.iloc[posicion].to_dict()
                )

        except Exception as e:

            self.mostrar_error(
                "Error al editar",
                str(e)
            )

    # ==================================================
    # ELIMINAR FILA
    # ==================================================

    def eliminar_fila(self, posicion_visual, indice_original):

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

            # REGISTRAR ELIMINACION

            self.cambios["eliminar"].append(
                indice_original
            )

            # ELIMINAR DE DATAFRAME FILTRADO

            self.df.drop(
                index=posicion_visual,
                inplace=True
            )

            self.df.reset_index(
                drop=True,
                inplace=True
            )
            
            # ACTUALIZAR MAPEO
            
            self._actualizar_mapeo_indices()

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
                f"No se logró eliminar el registro: {e}"
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

            import pandas as pd
            self.df = pd.concat(
                [
                    self.df,
                    pd.DataFrame([nueva_fila])
                ],
                ignore_index=True
            )
            
            # ACTUALIZAR MAPEO
            
            self._actualizar_mapeo_indices()

            # ACTUALIZAR TABLA

            self.modelo_tabla._df = self.df
            self.modelo_tabla.layoutChanged.emit()
            self.ui.tb_velada.resizeColumnsToContents()

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

            import pandas as pd
            df_actualizado = self.df_original.copy()

            if self.cambios["eliminar"]:
                df_actualizado = df_actualizado.drop(
                    self.cambios["eliminar"]
                )

            for indice_original, cambios_fila in self.cambios["editar"].items():

                for columna, nuevo_valor in cambios_fila.items():

                    df_actualizado.at[
                        indice_original,
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
                RUTA_VELADA,
                index=False
            )

            self.df = df_actualizado.copy()
            self.df_original = df_actualizado.copy()
            
            # ACTUALIZAR MAPEO TRAS GUARDAR
            
            self._actualizar_mapeo_indices()

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
            
            # ==========================================
            # ORDENAR POR FECHA_INICIO (MAS NUEVO A MAS VIEJO)
            # ==========================================
            
            if "Fecha Inicio" in self.df.columns:
                self.df = self.df.sort_values(
                    by="Fecha Inicio",
                    ascending=False
                ).copy()
            
            # RESETEAR INDICES
            
            self.df.reset_index(drop=True, inplace=True)
            
            # ACTUALIZAR MAPEO
            
            self._actualizar_mapeo_indices()

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