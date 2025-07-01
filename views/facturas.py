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
        self.tabla.setColumnCount(8)  # ✅ CAMBIAR DE 7 A 8 COLUMNAS
        self.tabla.setHorizontalHeaderLabels([
            "N° Factura", "Cliente", "Fecha", "Total", "Estado", "Subtotal", "Impuestos", "Saldo"  # ✅ AGREGAR SALDO
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
        self.tabla_pagos.setColumnCount(5)  # ✅ VOLVER A 5 COLUMNAS
        self.tabla_pagos.setHorizontalHeaderLabels([
            "Fecha", "Monto", "Método", "Observaciones", "Cliente"  # ✅ SIN SALDO
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

        # Botón para ver todos los pagos
        self.btn_ver_todos = QPushButton("Ver Todos los Pagos")
        self.btn_ver_todos.setObjectName("btnAzul")
        self.btn_ver_todos.clicked.connect(self.cargar_todos_los_pagos)  # ✅ MÉTODO SIMPLE
        btn_layout.addWidget(self.btn_ver_todos)

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
                
                # ✅ FECHA
                fecha_item = QTableWidgetItem(str(pago[5]))
                fecha_item.setTextAlignment(Qt.AlignCenter)
                self.tabla_pagos.setItem(row, 0, fecha_item)
                
                # ✅ MONTO
                monto_formateado = self.formatear_moneda(pago[3])
                monto_item = QTableWidgetItem(monto_formateado)
                monto_item.setTextAlignment(Qt.AlignCenter)
                self.tabla_pagos.setItem(row, 1, monto_item)
                
                # ✅ MÉTODO
                metodo_item = QTableWidgetItem(str(pago[4]))
                metodo_item.setTextAlignment(Qt.AlignCenter)
                self.tabla_pagos.setItem(row, 2, metodo_item)
                
                # ✅ OBSERVACIONES
                obs_item = QTableWidgetItem(str(pago[6]) if pago[6] else "")
                obs_item.setTextAlignment(Qt.AlignCenter)
                self.tabla_pagos.setItem(row, 3, obs_item)
                
                # ✅ CLIENTE
                cliente_item = QTableWidgetItem(str(pago[7]) if len(pago) > 7 else "")
                cliente_item.setTextAlignment(Qt.AlignCenter)
                self.tabla_pagos.setItem(row, 4, cliente_item)
                
        except Exception as e:
            print(f"Error cargando todos los pagos: {e}")

    def cargar_pagos_factura(self, factura_id):
        """Carga los pagos específicos de una factura seleccionada"""
        try:
            pagos = self.pagos_controller.get_pagos_por_factura_completo(factura_id)
            self.tabla_pagos.setRowCount(0)
            
            if not pagos:
                self.tabla_pagos.setRowCount(1)
                item = QTableWidgetItem("No hay pagos registrados para esta factura")
                item.setTextAlignment(Qt.AlignCenter)
                self.tabla_pagos.setItem(0, 0, item)
                self.tabla_pagos.setSpan(0, 0, 1, 5)  # ✅ VOLVER A 5 COLUMNAS
                return
            
            for pago in pagos:
                row = self.tabla_pagos.rowCount()
                self.tabla_pagos.insertRow(row)
                
                # ✅ FECHA
                fecha_item = QTableWidgetItem(str(pago[5]) if pago[5] else "")
                fecha_item.setTextAlignment(Qt.AlignCenter)
                self.tabla_pagos.setItem(row, 0, fecha_item)
                
                # ✅ MONTO
                monto_formateado = self.formatear_moneda(pago[3])
                monto_item = QTableWidgetItem(monto_formateado)
                monto_item.setTextAlignment(Qt.AlignCenter)
                self.tabla_pagos.setItem(row, 1, monto_item)
                
                # ✅ MÉTODO
                metodo_item = QTableWidgetItem(str(pago[4]) if pago[4] else "")
                metodo_item.setTextAlignment(Qt.AlignCenter)
                self.tabla_pagos.setItem(row, 2, metodo_item)
                
                # ✅ OBSERVACIONES
                obs_item = QTableWidgetItem(str(pago[6]) if pago[6] else "")
                obs_item.setTextAlignment(Qt.AlignCenter)
                self.tabla_pagos.setItem(row, 3, obs_item)
                
                # ✅ CLIENTE
                cliente_item = QTableWidgetItem(str(pago[7]) if pago[7] else "")
                cliente_item.setTextAlignment(Qt.AlignCenter)
                self.tabla_pagos.setItem(row, 4, cliente_item)
                
        except Exception as e:
            print(f"Error cargando pagos de factura {factura_id}: {e}")
            QMessageBox.warning(self, "Error", f"Error cargando pagos: {e}")

    def cargar_facturas(self):
        filtro = self.filtro_input.text()
        facturas = self.controller.get_facturas(filtro)
        self.tabla.setRowCount(0)
        
        # ✅ OBTENER IDS DE FACTURAS PARA CALCULAR SALDOS
        facturas_ids = [factura[0] for factura in facturas]  # factura[0] es el ID
        saldos = self.controller.calcular_saldos_multiples(facturas_ids)  # ✅ CALCULAR SALDOS
        
        for factura in facturas:
            row = self.tabla.rowCount()
            self.tabla.insertRow(row)
            
            # ✅ PRIMERAS 7 COLUMNAS (DATOS EXISTENTES)
            for col, value in enumerate(factura[1:8]):  # Solo las primeras 7 columnas para mostrar
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)
                
                # ✅ FORMATEAR COLUMNAS DE DINERO (Total, Subtotal, Impuestos)
                if col in [3, 5, 6]:  # Columnas: Total, Subtotal, Impuestos
                    try:
                        valor_numerico = float(value)
                        # Formato colombiano: $1.500,00
                        valor_formateado = self.formatear_moneda(valor_numerico)
                        item = QTableWidgetItem(valor_formateado)
                        item.setTextAlignment(Qt.AlignCenter)
                    except (ValueError, TypeError):
                        item = QTableWidgetItem(str(value))
                        item.setTextAlignment(Qt.AlignCenter)
                
                # Guarda el cliente_id en el UserRole de la columna 1 (Cliente)
                if col == 1:
                    item.setData(Qt.UserRole, factura[8])  # factura[8] es el cliente_id
                
                # Aplicar color amarillo a la columna de Estado si es "PENDIENTE"
                if col == 4 and str(value).upper() == "PENDIENTE":
                    item.setBackground(QColor(255, 255, 102))
                
                # Aplicar color verde a la columna de Estado si es "PAGADA"
                if col == 4 and str(value).upper() == "PAGADA":
                    item.setBackground(QColor(144, 238, 144))
                
                self.tabla.setItem(row, col, item)
            
            # ✅ COLUMNA 8: SALDO (NUEVA)
            factura_id = factura[0]  # ID de la factura
            saldo = saldos.get(factura_id, 0.0)
            saldo_formateado = self.formatear_moneda(saldo)
            saldo_item = QTableWidgetItem(saldo_formateado)
            saldo_item.setTextAlignment(Qt.AlignCenter)
            self.aplicar_color_saldo(saldo_item, saldo)  # ✅ APLICAR COLOR
            self.tabla.setItem(row, 7, saldo_item)  # ✅ COLUMNA 7 (índice 7)
            
            vh_item = QTableWidgetItem(str(factura[0]))
            vh_item.setTextAlignment(Qt.AlignCenter)
            self.tabla.setVerticalHeaderItem(row, vh_item)

    def agregar_factura(self):
        clientes = ClientesController().get_clientes()
        clientes_simple = [(c[0], c[1], c[2]) for c in clientes]
        dialog = FormularioFactura(clientes_simple, self)
        if dialog.exec_() == QDialog.Accepted:
            datos = dialog.get_data()
            productos = datos[-1]   
            pago_obs = datos[-2]
            pago_metodo = datos[-3]
            pago_monto = datos[-4]
            datos_factura = datos[:8]
            cliente_id = datos[1]

            if not productos:
                QMessageBox.warning(self, "Error", "Debe agregar al menos un producto.")
                return

            try:
                # ✅ GUARDAR FACTURA
                factura_id = self.controller.agregar_factura(*datos_factura)
                numero_factura = datos_factura[0]
                
                # ✅ AGREGAR PRODUCTOS A DETALLE_FACTURA
                from controllers.detalle_factura_controller import DetalleFacturaController
                detalle_controller = DetalleFacturaController()
                for producto in productos:
                    detalle_controller.agregar_detalle(
                        factura_id,
                        producto['item_id'],
                        producto['cantidad'],
                        producto['precio']
                    )
                
                # ✅ REGISTRAR PAGO SI SE INGRESÓ MONTO
                if pago_monto and float(pago_monto) > 0:
                    self.pagos_controller.registrar_pago(
                        cliente_id, factura_id, float(pago_monto), pago_metodo, pago_obs
                    )
                
                # ✅ ACTUALIZAR INTERFACES
                self.cargar_facturas()
                self.cargar_todos_los_pagos()
                QMessageBox.information(self, "Éxito", "Factura creada y pago registrado.")
                
            except Exception as e:
                print(f"❌ Error al crear factura: {e}")
                import traceback
                print(f"❌ Traceback: {traceback.format_exc()}")
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
    
    def nueva_factura(self):
        try:
            # ✅ TU CÓDIGO EXISTENTE SIN CAMBIOS
            clientes_controller = ClientesController()
            clientes = clientes_controller.get_clientes()
            
            if not clientes:
                QMessageBox.warning(self, "Advertencia", "No hay clientes registrados.")
                return
            
            dialog = FormularioFactura(clientes, self)
            if dialog.exec_() == QDialog.Accepted:
                data = dialog.get_data()
                if data:
                    # ✅ USAR TU CONTROLADOR COMO SIEMPRE
                    if self.controller.create_factura(*data[:8]):  # Solo los primeros 8 campos
                        QMessageBox.information(self, "Éxito", "Factura creada exitosamente.")
                        self.cargar_facturas()
                    else:
                        QMessageBox.critical(self, "Error", "No se pudo crear la factura.")
                        
        except Exception as e:
            print(f"Error creando factura: {e}")
            QMessageBox.critical(self, "Error", f"Error inesperado: {e}")

    def formatear_moneda(self, valor):
        """Formatear valor numérico como moneda colombiana"""
        try:
            valor_float = float(valor)
            # Formato colombiano: $1.500,00
            return f"${valor_float:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        except (ValueError, TypeError):
            return f"${valor}"

    def aplicar_color_saldo(self, item, saldo):
        """Aplicar color al item según el saldo"""
        try:
            if float(saldo) <= 0:
                # Saldo 0 o negativo = Verde (pagado)
                item.setBackground(QColor(144, 238, 144))
            else:
                # Saldo positivo = Amarillo (pendiente)
                item.setBackground(QColor(255, 255, 102))
        except (ValueError, TypeError):
            # Si no se puede convertir, no aplicar color
            pass
