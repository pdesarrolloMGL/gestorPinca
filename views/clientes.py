from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView
from PyQt5.QtCore import Qt
from data.connection import get_connection

class Clientes(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        titulo = QLabel("Cartera de Clientes")
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "N°", "Nombre", "Dirección", "Teléfono", "Saldado", "Deuda"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

        self.setLayout(layout)
        self.cargar_clientes()

    def cargar_clientes(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre, direccion, telefono, saldado, deuda FROM cartera_clientes")
        resultados = cursor.fetchall()
        self.table.setRowCount(len(resultados))
        for i, fila in enumerate(resultados):
            for j, valor in enumerate(fila):
                self.table.setItem(i, j, QTableWidgetItem(str(valor)))