from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QLineEdit, QLabel, QMessageBox, QHeaderView, QDialog, QFormLayout, QComboBox,
    QGroupBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QIcon
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

        # Título principal
        titulo = QLabel("Gestión de Facturas y Pagos")
        titulo.setObjectName("Titulo")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("""
            QLabel#Titulo {
                font-size: 22px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 18px;
            }
        """)
        layout.addWidget(titulo)

        # Filtro de búsqueda
        filtro_layout = QHBoxLayout()
        self.filtro_input = QLineEdit()
        self.filtro_input.setPlaceholderText("Buscar factura...")
        self.filtro_input.textChanged.connect(self.cargar_facturas)
        filtro_layout.addWidget(QLabel("Buscar:"))
        filtro_layout.addWidget(self.filtro_input)
        layout.addLayout(filtro_layout)

        # Layout horizontal para las dos tablas
        tablas_layout = QVBoxLayout()

        # Grupo de Facturas
        facturas_group = QGroupBox("FACTURAS")
        facturas_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                color: #000000;
                border: 2px solid #474747;
                border-radius: 10px;
                margin-top: 10px;
                margin-bottom: 10px;
                padding: 8px 4px 4px 4px;
            }
        """)
        facturas_layout = QVBoxLayout()

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
        self.tabla.setStyleSheet("""
            QTableWidget {
                background: #ffffff;
                border: 1px solid #bfc9d1;
                border-radius: 8px;
                font-size: 15px;
                selection-background-color: #0083CB;
                gridline-color: #bfc9d1;
            }
        """)
        # Conectar selección de factura para cargar pagos
        self.tabla.selectionModel().selectionChanged.connect(self.on_factura_seleccionada)
        
        facturas_layout.addWidget(self.tabla)
        facturas_group.setLayout(facturas_layout)
        tablas_layout.addWidget(facturas_group)  # Sin peso

        # Grupo de Historial de Pagos
        pagos_group = QGroupBox("HISTORIAL DE PAGOS")
        pagos_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                color: #000000;
                border: 2px solid #474747;
                border-radius: 10px;
                margin-top: 10px;
                margin-bottom: 10px;
                padding: 8px 4px 4px 4px;
            }
        """)
        pagos_layout = QVBoxLayout()

        # Tabla de pagos
        self.tabla_pagos = QTableWidget()
        self.tabla_pagos.setColumnCount(5)
        self.tabla_pagos.setHorizontalHeaderLabels([
            "Fecha", "Monto", "Método", "Observaciones", "Cliente"
        ])
        self.tabla_pagos.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla_pagos.verticalHeader().setVisible(False)
        self.tabla_pagos.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla_pagos.setStyleSheet("""
            QTableWidget {
                background: #ffffff;
                border: 1px solid #bfc9d1;
                border-radius: 8px;
                font-size: 15px;
                selection-background-color: #0083CB;
                gridline-color: #bfc9d1;
            }
        """)

        pagos_layout.addWidget(self.tabla_pagos)
        pagos_group.setLayout(pagos_layout)
        tablas_layout.addWidget(pagos_group)  # Sin peso

        layout.addLayout(tablas_layout)

        # Botones
        btn_layout = QHBoxLayout()
        self.btn_agregar = QPushButton("Agregar Factura")
        self.btn_agregar.setObjectName("btnVerde")
        self.btn_agregar.clicked.connect(self.agregar_factura)
        btn_layout.addWidget(self.btn_agregar)

        self.btn_eliminar = QPushButton("Eliminar Factura")
        self.btn_eliminar.setIcon(QIcon("assets/trash.png"))
        self.btn_eliminar.setObjectName("btnRojo")
        self.btn_eliminar.clicked.connect(self.eliminar_factura)
        btn_layout.addWidget(self.btn_eliminar)

        # Botón para registrar pago
        self.btn_registrar_pago = QPushButton("Registrar Pago")
        self.btn_registrar_pago.clicked.connect(self.registrar_pago_factura)
        btn_layout.addWidget(self.btn_registrar_pago)

        layout.addLayout(btn_layout)

        # Cargar datos iniciales
        self.cargar_facturas()
        self.cargar_todos_los_pagos()  # Cargar todos los pagos inicialmente

    def on_factura_seleccionada(self, selected, deselected):
        """Método que se ejecuta cuando se selecciona una factura"""
        indexes = selected.indexes()
        if indexes:
            row = indexes[0].row()
            factura_id = int(self.tabla.verticalHeaderItem(row).text())
            self.cargar_pagos_factura(factura_id)

    def cargar_todos_los_pagos(self):
        """Carga todos los pagos en la tabla de pagos"""
        try:
            pagos = self.pagos_controller.get_todos_los_pagos()
            self.tabla_pagos.setRowCount(0)
            for pago in pagos:
                row = self.tabla_pagos.rowCount()
                self.tabla_pagos.insertRow(row)
                # pago: (id, cliente_id, factura_id, monto, metodo_pago, fecha_pago, observaciones, nombre_cliente)
                self.tabla_pagos.setItem(row, 0, QTableWidgetItem(str(pago[5])))  # fecha_pago
                self.tabla_pagos.setItem(row, 1, QTableWidgetItem(f"${pago[3]:,.2f}"))  # monto
                self.tabla_pagos.setItem(row, 2, QTableWidgetItem(str(pago[4])))  # metodo_pago
                self.tabla_pagos.setItem(row, 3, QTableWidgetItem(str(pago[6]) if pago[6] else ""))  # observaciones
                self.tabla_pagos.setItem(row, 4, QTableWidgetItem(str(pago[7]) if len(pago) > 7 else ""))  # nombre_cliente
        except Exception as e:
            print(f"Error cargando todos los pagos: {e}")

    def cargar_pagos_factura(self, factura_id):
        """Carga los pagos específicos de una factura seleccionada"""
        try:
            pagos = self.pagos_controller.get_pagos_por_factura(factura_id)
            self.tabla_pagos.setRowCount(0)
            for pago in pagos:
                row = self.tabla_pagos.rowCount()
                self.tabla_pagos.insertRow(row)
                # pago: (id, cliente_id, factura_id, monto, metodo_pago, fecha_pago, observaciones, nombre_cliente)
                self.tabla_pagos.setItem(row, 0, QTableWidgetItem(str(pago[5])))  # fecha_pago
                self.tabla_pagos.setItem(row, 1, QTableWidgetItem(f"${pago[3]:,.2f}"))  # monto
                self.tabla_pagos.setItem(row, 2, QTableWidgetItem(str(pago[4])))  # metodo_pago
                self.tabla_pagos.setItem(row, 3, QTableWidgetItem(str(pago[6]) if pago[6] else ""))  # observaciones
                self.tabla_pagos.setItem(row, 4, QTableWidgetItem(str(pago[7]) if len(pago) > 7 else ""))  # nombre_cliente
        except Exception as e:
            print(f"Error cargando pagos de factura {factura_id}: {e}")

    def cargar_facturas(self):
        filtro = self.filtro_input.text()
        facturas = self.controller.get_facturas(filtro)
        self.tabla.setRowCount(0)
        for factura in facturas:
            row = self.tabla.rowCount()
            self.tabla.insertRow(row)
            for col, value in enumerate(factura[1:8]):  # Solo las primeras 7 columnas para mostrar
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)
                
                # Guarda el cliente_id en el UserRole de la columna 1 (Cliente)
                if col == 1:
                    item.setData(Qt.UserRole, factura[8])  # factura[8] es el cliente_id
                
                # Aplicar color amarillo a la columna de Subtotal (columna 5)
                if col == 4 and str(value).upper() == "PENDIENTE":  # Subtotal
                    item.setBackground(QColor(255, 255, 102))
                
                # Aplicar color verde a la columna de Estado si es "PAGADA" (columna 4)
                if col == 4 and str(value).upper() == "PAGADA":  # Estado
                    item.setBackground(QColor(144, 238, 144))
                
                self.tabla.setItem(row, col, item)
            vh_item = QTableWidgetItem(str(factura[0]))
            vh_item.setTextAlignment(Qt.AlignCenter)
            self.tabla.setVerticalHeaderItem(row, vh_item)

    def agregar_factura(self):
        clientes = ClientesController().get_clientes()
        clientes_simple = [(c[0], c[1], c[2]) for c in clientes]
        dialog = FormularioFactura(clientes_simple, self)
        if dialog.exec_() == QDialog.Accepted:
            datos = dialog.get_data()
            
            # Validar que se haya seleccionado un cliente
            if datos[1] is None:  # cliente_id
                QMessageBox.warning(self, "Error", "Debe seleccionar un cliente válido.")
                return
                
            productos = datos[-1]  # Lista de productos (último elemento)
            datos_factura = datos[:-1]  # Datos de la factura sin productos (primeros 8)
            
            # Validar que haya productos
            if not productos:
                QMessageBox.warning(self, "Error", "Debe agregar al menos un producto.")
                return
            
            try:
                # Crear la factura
                factura_id = self.controller.agregar_factura(*datos_factura)
                
                # Agregar productos y descontar inventario
                from controllers.detalle_factura_controller import DetalleFacturaController
                detalle_controller = DetalleFacturaController()
                
                for producto in productos:
                    detalle_controller.agregar_detalle(
                        factura_id,
                        producto['item_id'],
                        producto['cantidad'],
                        producto['precio']
                    )
                
                self.cargar_facturas()
                QMessageBox.information(self, "Éxito", "Factura creada y inventario actualizado.")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al crear factura: {str(e)}")

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
                self.cargar_facturas()  # Refresca la tabla de facturas
                self.cargar_todos_los_pagos()  # Refresca la tabla de pagos
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

        btn_guardar.clicked.connect(guardar)
        dialog.exec_()