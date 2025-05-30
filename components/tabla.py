from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView
import pandas as pd

class Tabla(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(self.sizePolicy().Expanding, self.sizePolicy().Expanding)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.verticalHeader().setVisible(False)
        self.setEditTriggers(QTableWidget.NoEditTriggers)  # Opcional: solo lectura

    def limpiar(self):
        self.clear()
        self.setRowCount(0)
        self.setColumnCount(0)

    def cargar_dataframe(self, df: pd.DataFrame):
        """Carga un DataFrame en la tabla, dejando celdas vacías si hay NaN."""
        self.limpiar()
        self.setRowCount(df.shape[0])
        self.setColumnCount(df.shape[1])
        self.setHorizontalHeaderLabels(df.columns)
        for i in range(df.shape[0]):
            for j in range(df.shape[1]):
                valor = df.iat[i, j]
                if pd.isna(valor):
                    valor = ""
                self.setItem(i, j, QTableWidgetItem(str(valor)))