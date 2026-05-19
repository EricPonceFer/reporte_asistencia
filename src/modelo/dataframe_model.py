import os
import pandas as pd


class CSVModel:

    def __init__(self):

        self.dataframe = pd.DataFrame()
        self.ruta_archivo = ""

    # =====================================================
    # CARGAR CSV
    # =====================================================

    def cargar_csv(
        self,
        ruta_archivo,
        separador=",",
        encoding="utf-8"
    ):

        try:

            # ==========================================
            # VALIDAR EXISTENCIA
            # ==========================================

            if not os.path.exists(ruta_archivo):

                raise FileNotFoundError(
                    "El archivo seleccionado no existe."
                )

            # ==========================================
            # VALIDAR EXTENSION
            # ==========================================
            ruta = str(ruta_archivo)

            if not ruta.endswith(".csv"):

                raise ValueError(
                    "El archivo debe tener extensión CSV."
                )

            # ==========================================
            # LEER CSV
            # ==========================================

            self.dataframe = pd.read_csv(
                ruta_archivo,
                sep=separador,
                encoding=encoding
            )

            self.ruta_archivo = ruta_archivo

            # ==========================================
            # VALIDAR VACIO
            # ==========================================

            if self.dataframe.empty:

                raise ValueError(
                    "El archivo CSV está vacío."
                )
            
            return self.dataframe

        except FileNotFoundError as error:
            raise Exception(str(error))

        except pd.errors.EmptyDataError:
            raise Exception(
                "El archivo CSV no contiene información."
            )

        except pd.errors.ParserError:
            raise Exception(
                "El archivo CSV tiene un formato inválido."
            )

        except UnicodeDecodeError:
            raise Exception(
                "Error de codificación. "
                "Intente usar otro encoding."
            )

        except Exception as error:
            raise Exception(
                f"No fue posible cargar el CSV:\n{error}"
            )

    # =====================================================
    # OBTENER DATAFRAME
    # =====================================================

    def obtener_dataframe(self):

        try:

            if self.dataframe.empty:

                raise Exception(
                    "No existen datos cargados."
                )

            return self.dataframe.copy()

        except Exception as error:
            raise Exception(str(error))

    # =====================================================
    # AGREGAR FILA
    # =====================================================

    def agregar_fila(self, datos):

        try:

            if self.dataframe.empty:

                raise Exception(
                    "Primero debe cargar un archivo CSV."
                )

            if not isinstance(datos, dict):

                raise Exception(
                    "Los datos deben enviarse "
                    "en formato diccionario."
                )

            # ==========================================
            # VALIDAR COLUMNAS
            # ==========================================

            columnas_faltantes = [

                columna

                for columna in self.dataframe.columns

                if columna not in datos

            ]

            if columnas_faltantes:

                raise Exception(
                    "Faltan columnas requeridas:\n"
                    f"{', '.join(columnas_faltantes)}"
                )

            nueva_fila = pd.DataFrame([datos])

            self.dataframe = pd.concat(
                [self.dataframe, nueva_fila],
                ignore_index=True
            )

            return self.dataframe

        except Exception as error:
            raise Exception(
                f"No fue posible agregar la fila:\n{error}"
            )

    # =====================================================
    # MODIFICAR FILA
    # =====================================================

    def modificar_fila(
        self,
        indice,
        columna,
        valor
    ):

        try:

            # ==========================================
            # VALIDAR DATAFRAME
            # ==========================================

            if self.dataframe.empty:

                raise Exception(
                    "No existen datos cargados."
                )

            # ==========================================
            # VALIDAR INDICE
            # ==========================================

            if indice not in self.dataframe.index:

                raise Exception(
                    "La fila seleccionada no existe."
                )

            # ==========================================
            # VALIDAR COLUMNA
            # ==========================================

            if columna not in self.dataframe.columns:

                raise Exception(
                    f"La columna '{columna}' no existe."
                )

            # ==========================================
            # MODIFICAR
            # ==========================================

            self.dataframe.at[
                indice,
                columna
            ] = valor

            return self.dataframe

        except Exception as error:
            raise Exception(
                f"No fue posible modificar la fila:\n{error}"
            )

    # =====================================================
    # ELIMINAR FILA
    # =====================================================

    def eliminar_fila(self, indice):

        try:

            if self.dataframe.empty:

                raise Exception(
                    "No existen datos cargados."
                )

            if indice not in self.dataframe.index:

                raise Exception(
                    "La fila seleccionada no existe."
                )

            self.dataframe = self.dataframe.drop(
                index=indice
            ).reset_index(drop=True)

            return self.dataframe

        except Exception as error:
            raise Exception(
                f"No fue posible eliminar la fila:\n{error}"
            )

    # =====================================================
    # GUARDAR CSV
    # =====================================================

    def guardar_csv(
        self,
        carpeta_guardado,
        nombre_archivo=None,
        separador=",",
        encoding="utf-8-sig"
    ):

        try:

            # ==========================================
            # VALIDAR DATAFRAME
            # ==========================================

            if self.dataframe.empty:

                raise Exception(
                    "No existen datos para guardar."
                )

            # ==========================================
            # VALIDAR CARPETA
            # ==========================================

            if not os.path.exists(carpeta_guardado):

                raise Exception(
                    "La carpeta de guardado no existe."
                )

            # ==========================================
            # NOMBRE ARCHIVO
            # ==========================================

            if not nombre_archivo:

                nombre_archivo = (
                    "archivo_generado.csv"
                )

            if not nombre_archivo.endswith(".csv"):

                nombre_archivo += ".csv"

            ruta_final = os.path.join(
                carpeta_guardado,
                nombre_archivo
            )

            # ==========================================
            # EXPORTAR
            # ==========================================

            self.dataframe.to_csv(
                ruta_final,
                index=False,
                sep=separador,
                encoding=encoding
            )

            return ruta_final

        except PermissionError:
            raise Exception(
                "El archivo está abierto. "
                "Ciérrelo e intente nuevamente."
            )

        except Exception as error:
            raise Exception(
                f"No fue posible guardar el CSV:\n{error}"
            )
