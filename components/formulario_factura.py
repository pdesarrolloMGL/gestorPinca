from PyQt5.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QComboBox, QDateEdit, QDoubleSpinBox, 
    QDialogButtonBox, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, 
    QTableWidgetItem, QSpinBox, QLabel, QGroupBox, QCheckBox, QSizePolicy, QHeaderView
)
from PyQt5.QtCore import QDate, Qt, QLocale
from controllers.inventario_controller import InventarioController

class FormularioFactura(QDialog):
    def __init__(self, clientes, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Crear Factura")
        self.setMinimumSize(700, 600)
        
        # Agregar estilo para fondo blanco
        self.setStyleSheet("""
            QDialog {
                background-color: white;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                background-color: white;
            }
            QLabel {
                background-color: white;
                color: black;
            }
            QLineEdit, QComboBox, QDateEdit, QSpinBox, QDoubleSpinBox {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                padding: 5px;
                background-color: white;
            }
            QTableWidget {
                background-color: white;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QCheckBox {
                background-color: white;
                color: black;
            }
        """)
        
        self.inventario_controller = InventarioController()
        
        layout = QVBoxLayout(self)

        # Datos básicos de la factura
        datos_group = QGroupBox("Datos de la Factura")
        form_layout = QFormLayout()

        self.input_numero = QLineEdit()
        
        self.combo_cliente = QComboBox()
        # No agregar "Sin cliente" - cliente requerido
        for cliente in clientes:
            nombre = f"{cliente[1]} / {cliente[2]}" if cliente[2] else cliente[1]
            self.combo_cliente.addItem(nombre, cliente[0])

        self.input_fecha = QDateEdit(QDate.currentDate())
        self.input_fecha.setCalendarPopup(True)
        
        # SELECT para estado
        self.combo_estado = QComboBox()
        self.combo_estado.addItems(["PENDIENTE", "PAGADA"])
        
        # CHECKBOX para IVA
        self.check_iva = QCheckBox("Incluir IVA (19%)")
        self.check_iva.setChecked(True)  # Por defecto marcado
        self.check_iva.stateChanged.connect(self.calcular_totales)

        form_layout.addRow("N° Factura:", self.input_numero)
        form_layout.addRow("Cliente:", self.combo_cliente)
        form_layout.addRow("Fecha:", self.input_fecha)
        form_layout.addRow("Estado:", self.combo_estado)
        form_layout.addRow("", self.check_iva)  # Checkbox sin label
        
        datos_group.setLayout(form_layout)
        layout.addWidget(datos_group)

        # Sección de productos
        productos_group = QGroupBox("Productos")
        productos_layout = QVBoxLayout()

        # Agregar producto
        agregar_layout = QHBoxLayout()
        self.combo_producto = QComboBox()
        self.cargar_productos()
        self.input_cantidad = QSpinBox()
        self.input_cantidad.setMinimum(1)
        self.input_cantidad.setMaximum(9999)

        # MEJORAS AL INPUT DE PRECIO
        self.input_precio = QDoubleSpinBox()
        self.input_precio.setMaximum(1e9)
        self.input_precio.setMinimum(0.01)
        self.input_precio.setPrefix("$ ")
        self.input_precio.setDecimals(2)
        self.input_precio.setSingleStep(100)
        self.input_precio.setMinimumWidth(120)
        self.input_precio.setMaximumWidth(150)
        self.input_precio.setAlignment(Qt.AlignCenter)

        # Configurar formato colombiano (punto para miles, coma para decimales)
        locale_colombiano = QLocale(QLocale.Spanish, QLocale.Colombia)
        self.input_precio.setLocale(locale_colombiano)

        # Configurar formato para mostrar separadores
        self.input_precio.setGroupSeparatorShown(True)  # Mostrar separador de miles

        self.input_precio.setValue(0.00)  # Valor inicial

        # Aplicar estilo específico al input precio
        self.input_precio.setStyleSheet("""
            QDoubleSpinBox {
                border: 2px solid #3498db;
                border-radius: 6px;
                padding: 8px;
                background-color: #f8f9fa;
                font-size: 14px;
                font-weight: bold;
                color: #2c3e50;
            }
            QDoubleSpinBox:focus {
                border: 2px solid #e74c3c;
                background-color: #ffffff;
            }
            QDoubleSpinBox:hover {
                border: 2px solid #27ae60;
                background-color: #ffffff;
            }
            QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
                width: 20px;
                border: none;
                background-color: #3498db;
                color: white;
            }
            QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {
                background-color: #2980b9;
            }
        """)

        # Mejorar estilo de cantidad
        self.input_cantidad.setStyleSheet("""
            QSpinBox {
                border: 2px solid #95a5a6;
                border-radius: 6px;
                padding: 8px;
                background-color: #f8f9fa;
                font-size: 14px;
                font-weight: bold;
                min-width: 80px;
                max-width: 100px;
            }
            QSpinBox:focus {
                border: 2px solid #3498db;
                background-color: #ffffff;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 20px;
                border: none;
                background-color: #95a5a6;
                color: white;
            }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                background-color: #7f8c8d;
            }
        """)

        # Mejorar estilo del combo producto
        self.combo_producto.setStyleSheet("""
            QComboBox {
                border: 2px solid #95a5a6;
                border-radius: 6px;
                padding: 8px;
                background-color: #f8f9fa;
                font-size: 14px;
                min-width: 200px;
            }
            QComboBox:focus {
                border: 2px solid #3498db;
                background-color: #ffffff;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                width: 12px;
                height: 12px;
            }
        """)

        self.btn_agregar_producto = QPushButton("Agregar Producto")
        self.btn_agregar_producto.clicked.connect(self.agregar_producto)

        # Mejorar estilo del botón agregar
        self.btn_agregar_producto.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 14px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
            QPushButton:pressed {
                background-color: #229954;
            }
        """)

        # Mejorar el layout del formulario de agregar producto
        agregar_layout.addWidget(QLabel("Producto:"))
        agregar_layout.addWidget(self.combo_producto, 2)  # Stretch factor 2
        agregar_layout.addWidget(QLabel("Cantidad:"))
        agregar_layout.addWidget(self.input_cantidad)
        agregar_layout.addWidget(QLabel("Precio:"))
        agregar_layout.addWidget(self.input_precio)
        agregar_layout.addWidget(self.btn_agregar_producto)
        
        productos_layout.addLayout(agregar_layout)

        # Tabla de productos agregados
        self.tabla_productos = QTableWidget()
        self.tabla_productos.setColumnCount(5)
        self.tabla_productos.setHorizontalHeaderLabels([
            "Producto", "Cantidad", "Precio", "Subtotal", "Eliminar"
        ])

        # Configurar para que ocupe todo el espacio disponible
        self.tabla_productos.setMinimumHeight(200)
        self.tabla_productos.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Configurar el ancho de las columnas
        header = self.tabla_productos.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Producto - ocupa el espacio restante
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Cantidad - ajuste al contenido
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Precio - ajuste al contenido
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Subtotal - ajuste al contenido
        header.setSectionResizeMode(4, QHeaderView.Fixed)  # Eliminar - ancho fijo
        header.resizeSection(4, 80)  # Ancho fijo de 80px para el botón eliminar

        productos_layout.addWidget(self.tabla_productos, 1)  # El "1" le da stretch factor

        productos_group.setLayout(productos_layout)
        layout.addWidget(productos_group)

        # Totales
        totales_group = QGroupBox("Totales")
        totales_layout = QFormLayout()
        
        self.label_subtotal = QLabel("$0.00")
        self.label_impuestos = QLabel("$0.00")
        self.label_total = QLabel("$0.00")
        
        # Hacer los labels más visibles
        self.label_subtotal.setStyleSheet("font-weight: bold; color: #2c3e50;")
        self.label_impuestos.setStyleSheet("font-weight: bold; color: #e74c3c;")
        self.label_total.setStyleSheet("font-weight: bold; font-size: 16px; color: #27ae60;")
        
        totales_layout.addRow("Subtotal:", self.label_subtotal)
        totales_layout.addRow("IVA (19%):", self.label_impuestos)
        totales_layout.addRow("Total:", self.label_total)
        
        totales_group.setLayout(totales_layout)
        layout.addWidget(totales_group)

        # Botones
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

        self.productos_factura = []  # Lista de productos agregados

    def cargar_productos(self):
        try:
            productos = self.inventario_controller.get_productos()
            for producto in productos:
                # producto: (id, nombre, descripcion, cantidad, precio, categoria_id)
                stock_text = f" (Stock: {producto[3]})" if len(producto) > 3 else ""
                self.combo_producto.addItem(f"{producto[1]}{stock_text}", producto[0])
        except Exception as e:
            print(f"Error cargando productos: {e}")

    def agregar_producto(self):
        if self.combo_producto.currentData() is None:
            return
            
        item_id = self.combo_producto.currentData()
        producto_nombre = self.combo_producto.currentText().split(" (Stock:")[0]
        cantidad = self.input_cantidad.value()
        precio = self.input_precio.value()
        
        if precio <= 0:
            return
            
        subtotal = cantidad * precio

        self.productos_factura.append({
            'item_id': item_id,
            'producto_nombre': producto_nombre,
            'cantidad': cantidad,
            'precio': precio,
            'subtotal': subtotal
        })

        self.actualizar_tabla_productos()
        self.calcular_totales()
        
        # Limpiar campos
        self.input_cantidad.setValue(1)
        self.input_precio.setValue(0.0)

    def actualizar_tabla_productos(self):
        self.tabla_productos.setRowCount(len(self.productos_factura))
        for row, producto in enumerate(self.productos_factura):
            self.tabla_productos.setItem(row, 0, QTableWidgetItem(producto['producto_nombre']))
            self.tabla_productos.setItem(row, 1, QTableWidgetItem(str(producto['cantidad'])))
            self.tabla_productos.setItem(row, 2, QTableWidgetItem(f"${producto['precio']:,.2f}"))
            self.tabla_productos.setItem(row, 3, QTableWidgetItem(f"${producto['subtotal']:,.2f}"))
            
            btn_eliminar = QPushButton("Eliminar")
            btn_eliminar.clicked.connect(lambda checked, r=row: self.eliminar_producto(r))
            self.tabla_productos.setCellWidget(row, 4, btn_eliminar)

    def eliminar_producto(self, row):
        del self.productos_factura[row]
        self.actualizar_tabla_productos()
        self.calcular_totales()

    def calcular_totales(self):
        subtotal = sum(p['subtotal'] for p in self.productos_factura)
        
        # Calcular IVA solo si está marcado el checkbox
        if self.check_iva.isChecked():
            impuestos = subtotal * 0.19  # 19% de IVA
        else:
            impuestos = 0.0
            
        total = subtotal + impuestos
        
        self.label_subtotal.setText(f"${subtotal:,.2f}")
        self.label_impuestos.setText(f"${impuestos:,.2f}")
        self.label_total.setText(f"${total:,.2f}")

    def get_data(self):
        subtotal = sum(p['subtotal'] for p in self.productos_factura)
        
        # Calcular IVA basado en el checkbox
        if self.check_iva.isChecked():
            impuestos = subtotal * 0.19
        else:
            impuestos = 0.0
            
        total = subtotal + impuestos
        
        return (
            self.input_numero.text(),
            self.combo_cliente.currentData(),
            self.input_fecha.date().toString("yyyy-MM-dd"),
            total,
            self.combo_estado.currentText(),  # Estado seleccionado
            subtotal,
            impuestos,
            0.0,  # Retención
            self.productos_factura  # Lista de productos
        )