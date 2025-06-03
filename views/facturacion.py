from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView
from PyQt5.QtCore import Qt
from data.connection import get_connection

class Facturacion(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        titulo = QLabel("Pantalla de Facturación")
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "N°", "Cliente ID", "Fecha", "Total", "Folio"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

        self.setLayout(layout)
        self.cargar_facturacion()

    def cargar_facturacion(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, cliente_id, fecha, total, folio FROM facturacion")
        resultados = cursor.fetchall()
        self.table.setRowCount(len(resultados))
        for i, fila in enumerate(resultados):
            for j, valor in enumerate(fila):
                self.table.setItem(i, j, QTableWidgetItem(str(valor)))
