from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QLineEdit, QLabel, QMessageBox, QHeaderView, QDialog
)
from PyQt5.QtCore import Qt
from controllers.facturas_controller import FacturasController
from components.formulario_factura import FormularioFactura
from controllers.clientes_controller import ClientesController

class Facturas(QWidget):
    def __init__(self):
        super().__init__()
        self.controller = FacturasController()
        self.setWindowTitle("Gestión de Facturas")

        layout = QVBoxLayout(self)

        # Filtro de búsqueda
        filtro_layout = QHBoxLayout()
        self.filtro_input = QLineEdit()
        self.filtro_input.setPlaceholderText("Buscar factura...")
        self.filtro_input.textChanged.connect(self.cargar_facturas)
        filtro_layout.addWidget(QLabel("Buscar:"))
        filtro_layout.addWidget(self.filtro_input)
        layout.addLayout(filtro_layout)

        # Tabla de facturas
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(7)
        self.tabla.setHorizontalHeaderLabels([
            "N° Factura", "Cliente", "Fecha", "Total", "Estado", "Subtotal", "Impuestos"
        ])
        self.tabla.horizontalHeader().setStretchLastSection(True)
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla.setSelectionMode(QTableWidget.SingleSelection)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setStyleSheet("background-color: white;")
        layout.addWidget(self.tabla)

        # Botones
        btn_layout = QHBoxLayout()
        self.btn_agregar = QPushButton("Agregar Factura")
        self.btn_agregar.clicked.connect(self.agregar_factura)
        btn_layout.addWidget(self.btn_agregar)

        self.btn_eliminar = QPushButton("Eliminar Factura")
        self.btn_eliminar.clicked.connect(self.eliminar_factura)
        btn_layout.addWidget(self.btn_eliminar)

        layout.addLayout(btn_layout)

        self.setLayout(layout)
        self.cargar_facturas()

    def cargar_facturas(self):
        filtro = self.filtro_input.text()
        facturas = self.controller.get_facturas(filtro)
        self.tabla.setRowCount(0)
        for factura in facturas:
            row = self.tabla.rowCount()
            self.tabla.insertRow(row)
            for col, value in enumerate(factura[1:]):  # Salta el id
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)
                self.tabla.setItem(row, col, item)
            vh_item = QTableWidgetItem(str(factura[0]))
            vh_item.setTextAlignment(Qt.AlignCenter)
            self.tabla.setVerticalHeaderItem(row, vh_item)

    def agregar_factura(self):
        # Obtén la lista de clientes
        clientes = ClientesController().get_clientes()
        # clientes: lista de tuplas (id, nombre_encargado, nombre_empresa, ...)
        clientes_simple = [(c[0], c[1], c[2]) for c in clientes]
        dialog = FormularioFactura(clientes_simple, self)
        if dialog.exec_() == QDialog.Accepted:
            datos = dialog.get_data()
            self.controller.agregar_factura(*datos)
            self.cargar_facturas()
            QMessageBox.information(self, "Éxito", "Factura agregada.")

    def eliminar_factura(self):
        row = self.tabla.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Eliminar", "Seleccione una factura para eliminar.")
            return
        factura_id = int(self.tabla.verticalHeaderItem(row).text())
        resp = QMessageBox.question(self, "Eliminar factura", "¿Seguro que desea eliminar esta factura?", QMessageBox.Yes | QMessageBox.No)
        if resp == QMessageBox.Yes:
            self.controller.eliminar_factura(factura_id)
            self.cargar_facturas()
            QMessageBox.information(self, "Eliminar", "Factura eliminada correctamente.")