from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QFileDialog, QHeaderView, QMessageBox, QHBoxLayout, QSizePolicy
)
from PyQt5.QtCore import Qt
import pandas as pd
import os

class Inventario(QWidget):
    def __init__(self):
        super().__init__()

        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        # Botones en una sola fila, centrados y de tamaño fijo
        botones_layout = QHBoxLayout()
        botones_layout.setAlignment(Qt.AlignCenter)

        # Botones para elegir la tabla
        botones_tabla_layout = QHBoxLayout()
        botones_tabla_layout.setAlignment(Qt.AlignCenter)
        
        btn_materia = QPushButton("Materia Prima")
        btn_materia.setObjectName("btnInventario")
        btn_materia.clicked.connect(self.mostrar_materia_prima)
        botones_tabla_layout.addWidget(btn_materia)

        btn_productos = QPushButton("Productos")
        btn_productos.setObjectName("btnInventario")
        btn_productos.clicked.connect(self.mostrar_productos)
        botones_tabla_layout.addWidget(btn_productos)

        main_layout.addLayout(botones_tabla_layout)

        btn_borrar = QPushButton("Eliminar fila seleccionada")
        btn_borrar.setStyleSheet(
            "background-color: #ffc107; color: black; border-radius: 8px; padding: 8px 16px;"
        )
        btn_borrar.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        btn_borrar.clicked.connect(self.eliminar_fila)
        botones_layout.addWidget(btn_borrar)

        main_layout.addLayout(botones_layout)

        # Tabla expandible y centrada
        self.table = QTableWidget()
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        main_layout.addWidget(self.table)

        # Ruta del Excel
        self.ruta_excel = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', 'data', 'DUPLICADOS.xlsx')
        )
        self.df = None

        # Cargar automáticamente el archivo al iniciar
        if os.path.exists(self.ruta_excel):
            self.df = pd.read_excel(self.ruta_excel)
            self.mostrar_datos(self.df)

    def mostrar_materia_prima(self):
        # Aquí debes poner la lógica para mostrar la tabla de materia prima
        if os.path.exists(self.ruta_excel):
            self.df = pd.read_excel(self.ruta_excel, sheet_name="MATERIAPRIMA")
            self.mostrar_datos(self.df)

    def mostrar_productos(self):
        # Aquí debes poner la lógica para mostrar la tabla de productos
        if os.path.exists(self.ruta_excel):
            self.df = pd.read_excel(self.ruta_excel, sheet_name="PRODUCTOS")
            self.mostrar_datos(self.df)

    def mostrar_datos(self, df):
        self.table.setRowCount(df.shape[0])
        self.table.setColumnCount(df.shape[1])
        self.table.setHorizontalHeaderLabels(df.columns)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # Formatear "Costo Unitario" como precio si existe
        try:
            idx_costo = df.columns.get_loc("Costo Unitario")
        except KeyError:
            idx_costo = -1
        for i in range(df.shape[0]):
            for j in range(df.shape[1]):
                valor = df.iat[i, j]
                if j == idx_costo and pd.notnull(valor):
                    try:
                        valor = "${:,.2f}".format(float(valor))
                    except Exception:
                        pass
                self.table.setItem(i, j, QTableWidgetItem(str(valor)))

    def eliminar_fila(self):
        fila = self.table.currentRow()
        if fila == -1:
            QMessageBox.warning(self, "Advertencia", "Selecciona una fila para eliminar.")
            return
        # Eliminar del DataFrame
        self.df = self.df.drop(self.df.index[fila]).reset_index(drop=True)
        # Guardar en Excel
        self.df.to_excel(self.ruta_excel, index=False)
        # Actualizar tabla
        self.mostrar_datos(self.df)