from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QLineEdit, QLabel, QMessageBox, QHeaderView, QDialog, QFormLayout, QComboBox
)
from PyQt5.QtCore import Qt
from controllers.facturas_controller import FacturasController
from components.formulario_factura import FormularioFactura
from controllers.clientes_controller import ClientesController
from controllers.pagos_cliente_controller import PagosClienteController

class Facturas(QWidget):
    def __init__(self):
        super().__init__()
        self.controller = FacturasController()
        self.pagos_controller = PagosClienteController()
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

        # Botón para registrar pago
        self.btn_registrar_pago = QPushButton("Registrar Pago")
        self.btn_registrar_pago.clicked.connect(self.registrar_pago_factura)
        btn_layout.addWidget(self.btn_registrar_pago)

        layout.addLayout(btn_layout)

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
                # Guarda el cliente_id en el UserRole de la columna 1 (Cliente)
                if col == 1:
                    item.setData(Qt.UserRole, factura[2])  # factura[2] debe ser el cliente_id
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

    def registrar_pago_factura(self):
        row = self.tabla.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Pago", "Seleccione una factura.")
            return
        factura_id = int(self.tabla.verticalHeaderItem(row).text())
        cliente_id = int(self.tabla.item(row, 1).data(Qt.UserRole))  # Ajusta según cómo guardes el cliente_id

        # Diálogo para ingresar monto y método
        dialog = QDialog(self)
        dialog.setWindowTitle("Registrar Pago")
        form = QFormLayout(dialog)  
        monto_input = QLineEdit()
        metodo_input = QComboBox()
        metodo_input.addItems(["Efectivo", "Transferencia", "Tarjeta", "Otro"])
        observaciones_input = QLineEdit()
        form.addRow("Monto:", monto_input)
        form.addRow("Método:", metodo_input)
        form.addRow("Observaciones:", observaciones_input)
        btn_guardar = QPushButton("Guardar")
        form.addRow(btn_guardar)

        def guardar():
            try:
                monto = float(monto_input.text())
                metodo = metodo_input.currentText()
                observaciones = observaciones_input.text()
                self.pagos_controller.registrar_pago(cliente_id, factura_id, monto, metodo, observaciones)
                QMessageBox.information(self, "Pago", "Pago registrado correctamente.")
                dialog.accept()
                self.cargar_facturas()  # Refresca la tabla si lo deseas
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

        btn_guardar.clicked.connect(guardar)
        dialog.exec_()