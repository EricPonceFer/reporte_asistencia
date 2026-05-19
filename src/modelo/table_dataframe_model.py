import pandas as pd

from PyQt6.QtCore import Qt, QAbstractTableModel


class DataFrameModel(QAbstractTableModel):

    def __init__(self, dataframe=pd.DataFrame()):
        super().__init__()
        self._df = dataframe

    def rowCount(self, parent=None):
        return self._df.shape[0]

    def columnCount(self, parent=None):
        return self._df.shape[1]

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):

        if role == Qt.ItemDataRole.DisplayRole:

            valor = self._df.iloc[index.row(), index.column()]
            return str(valor)

        return None

    def headerData(self, section, orientation, role):

        if role == Qt.ItemDataRole.DisplayRole:

            if orientation == Qt.Orientation.Horizontal:
                return str(self._df.columns[section])

            return str(self._df.index[section])

        return None