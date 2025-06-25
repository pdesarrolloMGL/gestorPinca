from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QLineEdit, QLabel, QMessageBox, QDialog, QHeaderView, QFileDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QIcon
from controllers.clientes_controller import ClientesController
from controllers.pagos_cliente_controller import PagosClienteController
from components.formulario_cliente import FormularioCliente
import csv

class Clientes(QWidget):
    def __init__(self):
        super().__init__()
        self.controller = ClientesController()
        self.pagos_controller = PagosClienteController()

        layout = QVBoxLayout(self)

        self.titulo_label = QLabel("Gestion de clientes")
        self.titulo_label.setAlignment(Qt.AlignCenter)
        self.titulo_label.setObjectName("tituloLabel")
        layout.addWidget(self.titulo_label)

        # Filtro de búsqueda
        filtro_layout = QHBoxLayout()
        self.filtro_input = QLineEdit()
        self.filtro_input.setPlaceholderText("Buscar cliente...")
        self.filtro_input.textChanged.connect(self.cargar_clientes)
        filtro_layout.addWidget(QLabel("Buscar:"))
        filtro_layout.addWidget(self.filtro_input)

        self.filtro_empresa = QLineEdit()
        self.filtro_empresa.setPlaceholderText("Empresa...")
        self.filtro_empresa.textChanged.connect(self.cargar_clientes)
        filtro_layout.addWidget(QLabel("Empresa:"))
        filtro_layout.addWidget(self.filtro_empresa)

        self.filtro_saldo = QLineEdit()
        self.filtro_saldo.setPlaceholderText("Saldo mayor a...")
        self.filtro_saldo.textChanged.connect(self.cargar_clientes)
        filtro_layout.addWidget(QLabel("Saldo >"))
        filtro_layout.addWidget(self.filtro_saldo)

        layout.addLayout(filtro_layout)

        # Tabla de clientes
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(6)
        self.tabla.setHorizontalHeaderLabels([
            "Cliente", "Empresa", "N° Documento", "Dirección", "Teléfono", "Email"
        ])
        self.tabla.horizontalHeader().setStretchLastSection(True)
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla.setSelectionMode(QTableWidget.SingleSelection)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setStyleSheet("background-color: white;")
        layout.addWidget(self.tabla)

        # Layout horizontal para las dos tablas (facturas y pagos)
        detalle_layout = QHBoxLayout()

        # Tabla de detalle de facturación
        self.tabla_detalle = QTableWidget()
        self.tabla_detalle.setColumnCount(6)
        self.tabla_detalle.setHorizontalHeaderLabels([
            "Factura", "Fecha", "Total", "Pagado", "Saldo", "Estado"
        ])
        self.tabla_detalle.horizontalHeader().setStretchLastSection(True)
        self.tabla_detalle.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla_detalle.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla_detalle.setSelectionMode(QTableWidget.SingleSelection)
        self.tabla_detalle.verticalHeader().setVisible(False)
        self.tabla_detalle.setStyleSheet("background-color: white;")
        detalle_layout.addWidget(self.tabla_detalle)

        # Tabla de historial de pagos
        self.tabla_pagos = QTableWidget()
        self.tabla_pagos.setColumnCount(4)
        self.tabla_pagos.setHorizontalHeaderLabels([
            "Fecha", "Monto", "Método", "Observaciones"
        ])
        self.tabla_pagos.horizontalHeader().setStretchLastSection(True)
        self.tabla_pagos.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla_pagos.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla_pagos.setSelectionMode(QTableWidget.SingleSelection)
        self.tabla_pagos.verticalHeader().setVisible(False)
        self.tabla_pagos.setStyleSheet("background-color: white;")
        detalle_layout.addWidget(self.tabla_pagos)

        layout.addLayout(detalle_layout)

        # Resumen de pagos
        self.resumen_label = QLabel("")
        layout.addWidget(self.resumen_label)
        self.tabla.itemSelectionChanged.connect(self.mostrar_resumen_cliente)

        # Botones
        btn_layout = QHBoxLayout()
        self.btn_agregar = QPushButton("Agregar Cliente")
        self.btn_agregar.setObjectName("btnVerde")
        self.btn_agregar.clicked.connect(self.agregar_cliente)
        btn_layout.addWidget(self.btn_agregar)

        self.btn_eliminar = QPushButton("Eliminar Cliente")
        self.btn_eliminar.setIcon(QIcon("assets/trash.png"))
        self.btn_eliminar.setObjectName("btnRojo")
        self.btn_eliminar.clicked.connect(self.eliminar_cliente)
        btn_layout.addWidget(self.btn_eliminar)

        self.btn_exportar = QPushButton("Exportar a CSV")
        self.btn_exportar.setObjectName("btnVerde")
        self.btn_exportar.clicked.connect(self.exportar_csv)
        btn_layout.addWidget(self.btn_exportar)

        layout.addLayout(btn_layout)

        self.setLayout(layout)

        self.cargar_clientes()

    def cargar_clientes(self):
        filtro = self.filtro_input.text()
        empresa = self.filtro_empresa.text()
        saldo = self.filtro_saldo.text()
        clientes = self.controller.get_clientes_avanzado(filtro, empresa, saldo)
        self.tabla.setRowCount(0)
        for cliente in clientes:
            row = self.tabla.rowCount()
            self.tabla.insertRow(row)
            for col, value in enumerate(cliente[1:]):  # Salta el id
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)
                self.tabla.setItem(row, col, item)
            vh_item = QTableWidgetItem(str(cliente[0]))
            vh_item.setTextAlignment(Qt.AlignCenter)
            self.tabla.setVerticalHeaderItem(row, vh_item)

    def mostrar_resumen_cliente(self):
        row = self.tabla.currentRow()
        if row < 0:
            self.resumen_label.setText("")
            self.tabla_detalle.setRowCount(0)
            self.tabla_pagos.setRowCount(0)
            return
        cliente_id = int(self.tabla.verticalHeaderItem(row).text())
        self.cargar_detalle_cliente(cliente_id)
        self.cargar_pagos_cliente(cliente_id)

    def agregar_cliente(self):
        dialog = FormularioCliente(self)
        if dialog.exec_() == QDialog.Accepted:
            datos = dialog.get_data()
            if not datos[0]:  # nombre_encargado obligatorio
                QMessageBox.warning(self, "Error", "El campo 'Encargado' es obligatorio.")
                return
            self.controller.agregar_cliente(*datos)
            self.cargar_clientes()
            QMessageBox.information(self, "Éxito", "Cliente agregado.")

    def eliminar_cliente(self):
        row = self.tabla.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Eliminar", "Seleccione un cliente para eliminar.")
            return
        cliente_id = int(self.tabla.verticalHeaderItem(row).text())
        resp = QMessageBox.question(self, "Eliminar cliente", "¿Seguro que desea eliminar este cliente?", QMessageBox.Yes | QMessageBox.No)
        if resp == QMessageBox.Yes:
            self.controller.eliminar_cliente(cliente_id)
            self.cargar_clientes()
            QMessageBox.information(self, "Eliminar", "Cliente eliminado correctamente.")

    def cargar_detalle_cliente(self, cliente_id):
        facturas = self.controller.get_facturas_cliente(cliente_id)
        self.tabla_detalle.setRowCount(0)
        for factura in facturas:
            factura_id, numero, fecha, total, estado = factura
            pagado = self.pagos_controller.total_pagado_factura(factura_id)
            saldo = round(total - pagado, 2)
            row = self.tabla_detalle.rowCount()
            self.tabla_detalle.insertRow(row)
            # Formatea los números como moneda
            total_str = "${:,.2f}".format(total)
            pagado_str = "${:,.2f}".format(pagado)
            saldo_str = "${:,.2f}".format(saldo)
            for col, value in enumerate([
                numero, fecha, total_str, pagado_str, saldo_str
            ]):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)
                self.tabla_detalle.setItem(row, col, item)
            estado_item = QTableWidgetItem(estado)
            estado_item.setTextAlignment(Qt.AlignCenter)
            if estado == "PAGADA":
                estado_item.setBackground(QColor(144, 238, 144))  # Verde claro
            elif estado == "PENDIENTE":
                estado_item.setBackground(QColor(255, 255, 102))  # Amarillo claro
            self.tabla_detalle.setItem(row, 5, estado_item)

    def cargar_pagos_cliente(self, cliente_id):
        pagos = self.pagos_controller.obtener_pagos_cliente(cliente_id)
        self.tabla_pagos.setRowCount(0)
        for pago in pagos:
            # pago: (id, factura_id, fecha_pago, monto, metodo_pago, observaciones)
            row = self.tabla_pagos.rowCount()
            self.tabla_pagos.insertRow(row)
            monto_str = "${:,.2f}".format(pago[3])
            for col, value in enumerate([
                pago[2], monto_str, pago[4], pago[5] or ""
            ]):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)
                self.tabla_pagos.setItem(row, col, item)

    def exportar_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Exportar clientes", "", "CSV Files (*.csv)")
        if not path:
            return
        with open(path, "w", newline='', encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Cliente", "Empresa", "N° Documento", "Dirección", "Teléfono", "Email"])
            for row in range(self.tabla.rowCount()):
                writer.writerow([self.tabla.item(row, col).text() for col in range(self.tabla.columnCount())])
        QMessageBox.information(self, "Exportar", "Clientes exportados correctamente.")