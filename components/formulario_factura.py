from PyQt5.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QComboBox, QDateEdit, QDoubleSpinBox, 
    QDialogButtonBox, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, 
    QTableWidgetItem, QSpinBox, QLabel, QGroupBox, QCheckBox, QSizePolicy, 
    QHeaderView, QFrame, QGridLayout
)
from PyQt5.QtCore import QDate, Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QFont
from controllers.inventario_controller import InventarioController
import locale
import re
from datetime import datetime

class InputMoneda(QLineEdit):
    valueChanged = pyqtSignal(float)
    
    def __init__(self):
        super().__init__()
        self.setPlaceholderText("$0,00")
        self.textChanged.connect(self.on_text_changed)
        self.setAlignment(Qt.AlignRight)
        self._value = 0.0
        self._updating = False  # ✅ BANDERA PARA EVITAR RECURSIÓN
        
    def on_text_changed(self, text):
        if self._updating:  # ✅ EVITAR BUCLE INFINITO
            return
            
        # ✅ EXTRAER SOLO NÚMEROS
        numeros = re.sub(r'[^\d]', '', text)
        
        if not numeros:
            self._value = 0.0
            self.valueChanged.emit(0.0)
            return
        
        try:
            # ✅ CONVERTIR A CENTAVOS Y LUEGO A PESOS
            valor_centavos = int(numeros)
            self._value = valor_centavos / 100.0
            self.valueChanged.emit(self._value)
            
            # ✅ FORMATEAR EN TIEMPO REAL
            self._updating = True  # Activar bandera
            formatted = f"${self._value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            
            # ✅ MANTENER POSICIÓN DEL CURSOR
            cursor_pos = self.cursorPosition()
            self.setText(formatted)
            # Ajustar cursor al final para mejor UX
            self.setCursorPosition(len(formatted))
            self._updating = False  # Desactivar bandera
            
        except ValueError:
            self._value = 0.0
            self.valueChanged.emit(0.0)
    
    def focusOutEvent(self, event):
        """Formatear cuando pierde el foco"""
        if self._value > 0:
            self._updating = True
            formatted = f"${self._value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            self.setText(formatted)
            self._updating = False
        super().focusOutEvent(event)
    
    def focusInEvent(self, event):
        """Seleccionar todo cuando gana foco para fácil edición"""
        super().focusInEvent(event)
        self.selectAll()  # ✅ SELECCIONAR TODO PARA FÁCIL REEMPLAZO
    
    def value(self):
        return self._value
    
    def setValue(self, valor):
        self._value = valor
        self._updating = True
        if valor > 0:
            formatted = f"${valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            self.setText(formatted)
        else:
            self.setText("")
        self._updating = False

class FormularioFactura(QDialog):
    def __init__(self, clientes, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nueva Factura")
        
        # Estilo minimalista mejorado
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 18px;
            }
            
            QGroupBox {
                font-weight: bold;
                font-size: 18px;
                color: #333333;
                border: 1px solid #cccccc;
                border-radius: 4px;
                margin-top: 15px;        /* ✅ MÁS ESPACIO ARRIBA */
                margin-bottom: 15px;     /* ✅ MÁS ESPACIO ABAJO */
                padding-top: 10px;       /* ✅ MÁS PADDING INTERNO */
                padding-bottom: 5px;     /* ✅ ESPACIO INTERNO ABAJO */
                background-color: #fafafa;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px;
                margin-bottom: 8px;      /* ✅ SEPARACIÓN DEL TÍTULO */
                background-color: transparent;
                color: #333333;
            }
            
            QLineEdit, QComboBox, QDateEdit, QSpinBox {
                border: 1px solid #cccccc;
                border-radius: 3px;
                padding: 6px;
                background-color: #ffffff;
                font-size: 18px;
            }
            
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QSpinBox:focus {
                border: 1px solid #4a90e2;
            }
            
            QTableWidget {
                background-color: #ffffff;
                border: 1px solid #cccccc;
                gridline-color: #e0e0e0;
                font-size: 18px;
            }
            
            QTableWidget::item {
                padding: 4px;
                border: none;
            }
            
            QTableWidget::item:selected {
                background-color: #e3f2fd;
            }
            
            QHeaderView::section {
                background-color: #f5f5f5;
                color: #333333;
                padding: 6px;
                border: 1px solid #cccccc;
                font-weight: bold;
                font-size: 18px;
            }
            
            /* ✅ CHECKBOX SIMPLE Y FUNCIONAL */
            QCheckBox {
                color: #333333;
                font-size: 18px;
                spacing: 8px;
                background-color: transparent;
            }
            
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #cccccc;
                border-radius: 3px;
                background-color: #ffffff;
            }
            
            QCheckBox::indicator:hover {
                border: 2px solid #4a90e2;
                background-color: #f8f9fa;
            }
            
            QCheckBox::indicator:checked {
                background-color: #4a90e2;
                border: 2px solid #4a90e2;
            }
            
            QLabel {
                color: #333333;
                font-size: 18px;
                background-color: transparent;
            }
            
            QLabel#total {
                font-size: 18px;
                font-weight: bold;
                color: #2e7d32;
                background-color: #e8f5e8;
                padding: 8px;
                border: 1px solid #4caf50;
                border-radius: 3px;
            }
            QPushButton#btnFactura {
            background-color: #28a745;
            color: white;
            border-radius: 5px;
            padding: 10px 12px;
        }
        """)
        
        self.inventario_controller = InventarioController()
        self.productos_factura = []
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(8)
        main_layout.setContentsMargins(12, 12, 12, 12)
        
        # Layout principal horizontal
        content_layout = QHBoxLayout()
        
        # Columna izquierda
        left_column = QVBoxLayout()
        left_column.setSpacing(8)
        
        # Información de factura
        info_group = QGroupBox("Información de Factura")
        info_layout = QGridLayout()
        info_layout.setSpacing(8)
        
        # ✅ FILA 1 - NÚMERO Y FECHA
        info_layout.addWidget(QLabel("Número:"), 0, 0)
        self.input_numero = QLineEdit()
        
        # ✅ HACER EL CAMPO SOLO LECTURA
        self.input_numero.setReadOnly(True)
        self.input_numero.setStyleSheet("""
            QLineEdit {
                background-color: #f8f9fa;
                color: #495057;
                font-weight: bold;
                border: 1px solid #ced4da;
            }
            QLineEdit:focus {
                border: 1px solid #ced4da;
                background-color: #f8f9fa;
            }
        """)
        
        # ✅ GENERAR NÚMERO AUTOMÁTICAMENTE AL INICIALIZAR
        self.generar_numero_factura()
        
        info_layout.addWidget(self.input_numero, 0, 1)
        
        # ✅ BOTÓN REGENERAR
        btn_regenerar = QPushButton("🔄")
        btn_regenerar.setMaximumWidth(35)
        btn_regenerar.setMaximumHeight(30)
        btn_regenerar.setToolTip("Regenerar número de factura")
        btn_regenerar.setObjectName("btnRefrescar")
        btn_regenerar.clicked.connect(self.generar_numero_factura)  # ✅ CONECTAR AL MÉTODO
        info_layout.addWidget(btn_regenerar, 0, 2)
        
        # ✅ FECHA EN LA MISMA FILA
        info_layout.addWidget(QLabel("Fecha:"), 0, 3)
        self.input_fecha = QDateEdit(QDate.currentDate())
        self.input_fecha.setCalendarPopup(True)
        info_layout.addWidget(self.input_fecha, 0, 4)
        
        # ✅ FILA 2 - CLIENTE Y ESTADO
        info_layout.addWidget(QLabel("Cliente:"), 1, 0)
        self.combo_cliente = QComboBox()
        self.combo_cliente.setMinimumWidth(500)  # ✅ Más ancho
        for cliente in clientes:
            nombre = f"{cliente[1]} - {cliente[2]}" if cliente[2] else cliente[1]
            self.combo_cliente.addItem(nombre, cliente[0])
        info_layout.addWidget(self.combo_cliente, 1, 1, 1, 3)  # Ocupa 3 columnas
        
        info_layout.addWidget(QLabel("Estado:"), 1, 4)
        self.label_estado = QLabel("PENDIENTE")
        self.label_estado.setStyleSheet("""
            QLabel {
                background-color: #fff3cd;
                color: #856404;
                border: 1px solid #ffeaa7;
                border-radius: 3px;
                padding: 6px;
                font-weight: bold;
            }
        """)
        info_layout.addWidget(self.label_estado, 1, 4)
        
        info_group.setLayout(info_layout)
        left_column.addWidget(info_group)
        
        # Pago inicial
        pago_group = QGroupBox("Pago Inicial (Opcional)")
        pago_layout = QGridLayout()
        pago_layout.setSpacing(8)
        
        pago_layout.addWidget(QLabel("Monto:"), 0, 0)
        self.pago_monto_input = InputMoneda()
        # ✅ CONECTAR CAMBIOS EN PAGO PARA RECALCULAR ESTADO
        self.pago_monto_input.valueChanged.connect(self.calcular_estado_por_pago)
        pago_layout.addWidget(self.pago_monto_input, 0, 1)
        
        pago_layout.addWidget(QLabel("Método:"), 0, 2)
        self.pago_metodo_input = QComboBox()
        self.pago_metodo_input.addItems(["EFECTIVO", "TRANSFERENCIA", "TARJETA", "OTRO"])
        pago_layout.addWidget(self.pago_metodo_input, 0, 3)
        
        pago_layout.addWidget(QLabel("Observaciones:"), 1, 0)
        self.pago_obs_input = QLineEdit()
        self.pago_obs_input.setPlaceholderText("Observaciones del pago...")
        pago_layout.addWidget(self.pago_obs_input, 1, 1, 1, 3)
        
        pago_group.setLayout(pago_layout)
        left_column.addWidget(pago_group)
        
        # Agregar producto
        producto_group = QGroupBox("Agregar Producto")
        producto_layout = QGridLayout()
        producto_layout.setSpacing(8)
        
        producto_layout.addWidget(QLabel("Producto:"), 0, 0)
        self.combo_producto = QComboBox()
        self.combo_producto.setMinimumWidth(250)
        self.cargar_productos()
        producto_layout.addWidget(self.combo_producto, 0, 1, 1, 2)
        
        producto_layout.addWidget(QLabel("Cantidad:"), 1, 0)
        self.input_cantidad = QSpinBox()
        self.input_cantidad.setMinimum(1)
        self.input_cantidad.setMaximum(9999)
        self.input_cantidad.setValue(1)
        producto_layout.addWidget(self.input_cantidad, 1, 1)
        
        producto_layout.addWidget(QLabel("Precio:"), 1, 2)
        self.input_precio = InputMoneda()
        self.input_precio.valueChanged.connect(self.calcular_totales)
        producto_layout.addWidget(self.input_precio, 1, 3)
        
        self.btn_agregar_producto = QPushButton("Agregar")
        self.btn_agregar_producto.setObjectName("btnFactura")
        self.btn_agregar_producto.clicked.connect(self.agregar_producto)
        producto_layout.addWidget(self.btn_agregar_producto, 1, 4)
        
        producto_group.setLayout(producto_layout)
        left_column.addWidget(producto_group)
        
        # Totales
        totales_group = QGroupBox("Totales")
        totales_layout = QGridLayout()
        totales_layout.setSpacing(8)
        
        # Modificar el checkbox IVA para recalcular estado
        self.check_iva = QCheckBox("Incluir IVA (19%)")
        self.check_iva.setChecked(True)
        self.check_iva.stateChanged.connect(self.calcular_totales)
        totales_layout.addWidget(self.check_iva, 0, 0, 1, 2)
        
        totales_layout.addWidget(QLabel("Subtotal:"), 1, 0)
        self.label_subtotal = QLabel("0.00")
        self.label_subtotal.setAlignment(Qt.AlignRight)
        totales_layout.addWidget(self.label_subtotal, 1, 1)
        
        totales_layout.addWidget(QLabel("IVA:"), 2, 0)
        self.label_impuestos = QLabel("0.00")
        self.label_impuestos.setAlignment(Qt.AlignRight)
        totales_layout.addWidget(self.label_impuestos, 2, 1)
        
        totales_layout.addWidget(QLabel("TOTAL:"), 3, 0)
        self.label_total = QLabel("0.00")
        self.label_total.setObjectName("total")
        self.label_total.setAlignment(Qt.AlignRight)
        totales_layout.addWidget(self.label_total, 3, 1)
        
        totales_group.setLayout(totales_layout)
        left_column.addWidget(totales_group)
        
        left_column.addStretch()
        
        # Columna derecha - Tabla de productos
        right_column = QVBoxLayout()
        right_column.setSpacing(8)  # ✅ AGREGAR ESPACIADO
        
        productos_group = QGroupBox("Productos de la Factura")
        productos_layout = QVBoxLayout()
        productos_layout.setContentsMargins(8, 8, 8, 8)  # ✅ MÁRGENES INTERNOS
        
        self.tabla_productos = QTableWidget()
        self.tabla_productos.setColumnCount(5)
        self.tabla_productos.setHorizontalHeaderLabels([
            "Producto", "Cantidad", "Precio", "Subtotal", "Eliminar"
        ])
        self.tabla_productos.setMinimumHeight(400)
        
        # ✅ CONFIGURAR POLÍTICA DE TAMAÑO PARA QUE USE TODO EL ESPACIO
        self.tabla_productos.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Configurar columnas con mejor distribución
        header = self.tabla_productos.horizontalHeader()
        
        # ✅ CONFIGURACIÓN MEJORADA DE COLUMNAS
        header.setSectionResizeMode(0, QHeaderView.Stretch)        # Producto - Ocupa espacio restante
        header.setSectionResizeMode(1, QHeaderView.Fixed)          # Cantidad - Tamaño fijo
        header.setSectionResizeMode(2, QHeaderView.Fixed)          # Precio - Tamaño fijo
        header.setSectionResizeMode(3, QHeaderView.Fixed)          # Subtotal - Tamaño fijo
        header.setSectionResizeMode(4, QHeaderView.Fixed)          # Acciones - Tamaño fijo
        
        # ✅ ESTABLECER ANCHOS ESPECÍFICOS
        self.tabla_productos.setColumnWidth(1, 80)   # Cantidad
        self.tabla_productos.setColumnWidth(2, 130)  # Precio
        self.tabla_productos.setColumnWidth(3, 130)  # Subtotal
        self.tabla_productos.setColumnWidth(4, 90)   # Eliminar
        
        # ✅ CONFIGURACIONES ADICIONALES
        header.setMinimumSectionSize(60)
        header.setDefaultSectionSize(100)
        header.setStretchLastSection(False)  # No estirar la última columna
        
        self.tabla_productos.verticalHeader().setVisible(False)
        
        # ✅ ASEGURAR QUE LA TABLA SE EXPANDA HORIZONTALMENTE
        self.tabla_productos.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.tabla_productos.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        productos_layout.addWidget(self.tabla_productos)
        productos_group.setLayout(productos_layout)
        right_column.addWidget(productos_group)
        
        # Agregar columnas al layout principal con mejor proporción
        content_layout.addLayout(left_column, 2)    # ✅ Columna izquierda MÁS ANCHA
        content_layout.addLayout(right_column, 2)   # ✅ Columna derecha proporcionalmente ajustada
        
        main_layout.addLayout(content_layout)
        
        # Botones
        botones_layout = QHBoxLayout()
        botones_layout.addStretch()
        
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setObjectName("btnRojo")
        btn_cancelar.clicked.connect(self.reject)
        botones_layout.addWidget(btn_cancelar)
        
        btn_guardar = QPushButton("Guardar")
        btn_guardar.setObjectName("btnRefrescar")
        btn_guardar.clicked.connect(self.accept)
        botones_layout.addWidget(btn_guardar)
        
        main_layout.addLayout(botones_layout)

        # ✅ CONFIGURAR TAMAÑO Y POSICIÓN CON setGeometry()
        screen_geometry = self.screen().geometry()
        width = int(screen_geometry.width() * 0.75)
        height = int(screen_geometry.height() * 0.80)
        
        # Calcular posición centrada
        x = (screen_geometry.width() - width) // 2
        y = (screen_geometry.height() - height) // 2
        
        # Establecer geometría (posición y tamaño)
        self.setGeometry(x, y, width, height)

    def cargar_productos(self):
        try:
            productos = self.inventario_controller.get_productos()
            for producto in productos:
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
        # ✅ YA NO ES NECESARIO LLAMAR calcular_estado() AQUÍ PORQUE SE LLAMA EN calcular_totales()
        
        # Limpiar campos
        self.input_cantidad.setValue(1)
        self.input_precio.setValue(0.0)

    def actualizar_tabla_productos(self):
        self.tabla_productos.setRowCount(len(self.productos_factura))
        for row, producto in enumerate(self.productos_factura):
            self.tabla_productos.setItem(row, 0, QTableWidgetItem(producto['producto_nombre']))
            self.tabla_productos.setItem(row, 1, QTableWidgetItem(str(producto['cantidad'])))
            
            # Formatear precios
            precio_formateado = f"{producto['precio']:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            subtotal_formateado = f"{producto['subtotal']:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            
            precio_item = QTableWidgetItem(precio_formateado)
            precio_item.setTextAlignment(Qt.AlignRight)
            self.tabla_productos.setItem(row, 2, precio_item)
            
            subtotal_item = QTableWidgetItem(subtotal_formateado)
            subtotal_item.setTextAlignment(Qt.AlignRight)
            self.tabla_productos.setItem(row, 3, subtotal_item)
            
            btn_eliminar = QPushButton("")
            btn_eliminar.setObjectName("btnRojo")
            btn_eliminar.setIcon(QIcon("assets/trash.png"))
            btn_eliminar.setToolTip("Eliminar")
            btn_eliminar.clicked.connect(lambda checked, r=row: self.eliminar_producto(r))
            self.tabla_productos.setCellWidget(row, 4, btn_eliminar)

    def eliminar_producto(self, row):
        del self.productos_factura[row]
        self.actualizar_tabla_productos()
        self.calcular_totales()
        # ✅ YA NO ES NECESARIO LLAMAR calcular_estado() AQUÍ PORQUE SE LLAMA EN calcular_totales()

    # ✅ MEJORAR MÉTODO: CALCULAR ESTADO AUTOMÁTICAMENTE
    def calcular_estado(self):
        """Calcular el estado de la factura basado en el saldo"""
        try:
            # Calcular total de la factura
            subtotal = sum(p['subtotal'] for p in self.productos_factura)
            
            # ✅ SI NO HAY PRODUCTOS, MANTENER ESTADO PENDIENTE
            if not self.productos_factura or subtotal == 0:
                estado = "PENDIENTE"
                self.label_estado.setText(estado)
                self.label_estado.setStyleSheet("""
                    QLabel {
                        background-color: #fff3cd;
                        color: #856404;
                        border: 1px solid #ffeaa7;
                        border-radius: 3px;
                        padding: 6px;
                        font-weight: bold;
                    }
                """)
                return
            
            if self.check_iva.isChecked():
                impuestos = subtotal * 0.19
            else:
                impuestos = 0.0
                
            total_factura = subtotal + impuestos
            
            # Obtener pago inicial
            pago_inicial = self.pago_monto_input.value()
            
            # Calcular saldo pendiente
            saldo_pendiente = total_factura - pago_inicial
            
            # Determinar estado basado en el saldo
            if saldo_pendiente <= 0 and total_factura > 0:  # ✅ ASEGURAR QUE HAY TOTAL > 0
                estado = "PAGADA"
                self.label_estado.setText(estado)
                self.label_estado.setStyleSheet("""
                    QLabel {
                        background-color: #d4edda;
                        color: #155724;
                        border: 1px solid #c3e6cb;
                        border-radius: 3px;
                        padding: 6px;
                        font-weight: bold;
                    }
                """)
            else:
                estado = "PENDIENTE"
                self.label_estado.setText(estado)
                self.label_estado.setStyleSheet("""
                    QLabel {
                        background-color: #fff3cd;
                        color: #856404;
                        border: 1px solid #ffeaa7;
                        border-radius: 3px;
                        padding: 6px;
                        font-weight: bold;
                    }
                """)
                
        except Exception as e:
            print(f"Error calculando estado: {e}")
            self.label_estado.setText("PENDIENTE")
            self.label_estado.setStyleSheet("""
                QLabel {
                    background-color: #fff3cd;
                    color: #856404;
                    border: 1px solid #ffeaa7;
                    border-radius: 3px;
                    padding: 6px;
                    font-weight: bold;
                }
            """)
    
    def calcular_totales(self):
        subtotal = sum(p['subtotal'] for p in self.productos_factura)
        
        if self.check_iva.isChecked():
            impuestos = subtotal * 0.19
        else:
            impuestos = 0.0
            
        total = subtotal + impuestos
        
        # Formatear con formato colombiano
        self.label_subtotal.setText(f"{subtotal:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        self.label_impuestos.setText(f"{impuestos:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        self.label_total.setText(f"{total:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        
        # ✅ SOLO RECALCULAR ESTADO SI HAY PRODUCTOS
        if self.productos_factura:
            self.calcular_estado()

    # ✅ CREAR MÉTODO ESPECÍFICO PARA CAMBIOS EN PAGO
    def calcular_estado_por_pago(self):
        """Recalcular estado solo cuando cambia el pago"""
        if self.productos_factura:  # Solo si hay productos
            self.calcular_estado()
    
    def generar_numero_factura(self):
        """Generar número de factura automáticamente"""
        try:
            import random
            from datetime import datetime
            
            # ✅ GENERAR NÚMERO COMPLETAMENTE AL AZAR
            numero_aleatorio = random.randint(10000000, 99999999)  # 8 dígitos
            numero_generado = f"F-{numero_aleatorio}"
            
            # ✅ VERIFICAR QUE NO EXISTA (OPCIONAL)
            from controllers.facturas_controller import FacturasController
            controller = FacturasController()
            
            # Si existe, generar otro
            max_intentos = 10
            for intento in range(max_intentos):
                if not controller.existe_numero_factura(numero_generado):
                    break
                numero_aleatorio = random.randint(10000000, 99999999)
                numero_generado = f"F-{numero_aleatorio}"
            
            self.input_numero.setText(numero_generado)
            print(f"Número generado: {numero_generado}")
            
        except Exception as e:
            print(f"Error generando número de factura: {e}")
            # ✅ FALLBACK SIMPLE CON TIMESTAMP
            import random
            numero_fallback = f"F-{random.randint(10000000, 99999999)}"
            self.input_numero.setText(numero_fallback)
            print(f"Número fallback: {numero_fallback}")

    # ✅ TU MÉTODO get_data EXISTENTE (sin cambios)
    def get_data(self):
        """Devolver datos del formulario"""
        subtotal = sum(p['subtotal'] for p in self.productos_factura)
        
        if self.check_iva.isChecked():
            impuestos = subtotal * 0.19
        else:
            impuestos = 0.0
            
        total = subtotal + impuestos
        estado_calculado = self.label_estado.text()
        
        pago_monto_str = f"{self.pago_monto_input.value():.2f}" if self.pago_monto_input.value() > 0 else "0.00"
        pago_metodo = self.pago_metodo_input.currentText()
        pago_observaciones = self.pago_obs_input.text()

        return (
            self.input_numero.text(),  # ✅ USA EL NÚMERO GENERADO
            self.combo_cliente.currentData(),
            self.input_fecha.date().toString("yyyy-MM-dd"),
            total,
            estado_calculado,
            subtotal,
            impuestos,
            0.0,  # descuento
            pago_monto_str,
            pago_metodo,
            pago_observaciones,
            self.productos_factura
        )