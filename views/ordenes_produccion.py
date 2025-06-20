from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox, QTableWidget, QTableWidgetItem,
    QHBoxLayout, QPushButton, QLineEdit, QHeaderView, QMessageBox, QGroupBox, QFrame, QDateEdit
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QColor
from controllers.ordenes_produccion_controller import OrdenesProduccionController

class OrdenesProduccion(QWidget):
    def __init__(self):
        super().__init__()
        self.controller = OrdenesProduccionController()

        self.setStyleSheet("""
            QComboBox {
                min-width: 220px;
                max-width: 350px;
                padding: 7px 12px;
                border: 1px solid #ced4da;
                border-radius: 8px;
                background: #fff;
                color: #474747;
                font-size: 15px;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #ced4da;
                selection-background-color: #474747;
                font-size: 15px;
            }
            QLineEdit {
                background-color: #fff;
                border: 1px solid #bfc9d1;
                border-radius: 4px;
                padding: 6px 10px;
                font-size: 15px;
                color: #474747;
            }
            QPushButton#btnNuevaOrden {
                background-color: #3498db;
                color: white;
                border-radius: 8px;
                padding: 10px 24px;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton#btnNuevaOrden:hover {
                background-color: #217dbb;
            }
            QPushButton#btnVerCostos {
                background-color: #28a745;
                color: white;
                border-radius: 8px;
                padding: 10px 24px;
                font-size: 15px;
                font-weight: bold;
                margin-left: 8px;
            }
            QPushButton#btnVerCostos:hover {
                background-color: #218838;
                color: white;
            }
            QGroupBox {
                font-weight: bold;
                color: #000000;
                border: 2px solid #474747;
                border-radius: 10px;
                margin-top: 10px;
                margin-bottom: 10px;
                padding: 8px 4px 4px 4px;
            }
            QTableWidget {
                background: #ffffff;
                border: 1px solid #bfc9d1;
                border-radius: 8px;
                font-size: 15px;
                selection-background-color: #0083CB;
                gridline-color: #bfc9d1;
            }
            QLabel#ResumenCostos {
                background: #ffffff;
                border: 1.5px solid #dbdbdb;
                border-radius: 8px;
                padding: 18px 24px;
                font-size: 16px;
            }
            QLabel#Titulo {
                font-size: 22px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 18px;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignTop)

        # Título
        titulo = QLabel("Órdenes de Producción")
        titulo.setObjectName("Titulo")
        titulo.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(titulo)

        # Selector de producto y botones
        selector_layout = QHBoxLayout()
        self.producto_combo = QComboBox()
        self.productos = self.controller.get_productos()
        self.producto_combo.addItem("Seleccione producto...", None)
        for prod in self.productos:
            self.producto_combo.addItem(prod[1], prod[0])
        selector_layout.addWidget(self.producto_combo)

        self.cantidad_input = QLineEdit()
        self.cantidad_input.setPlaceholderText("Cantidad a producir")
        selector_layout.addWidget(self.cantidad_input)

        self.btn_nueva_orden = QPushButton("Crear Orden")
        self.btn_nueva_orden.setObjectName("btnNuevaOrden")
        self.btn_nueva_orden.clicked.connect(self.crear_orden)
        selector_layout.addWidget(self.btn_nueva_orden)

        self.btn_ver_costos = QPushButton("Ver Costos de Producción")
        self.btn_ver_costos.setObjectName("btnVerCostos")
        self.btn_ver_costos.clicked.connect(self.ver_costos_orden)
        selector_layout.addWidget(self.btn_ver_costos)

        main_layout.addLayout(selector_layout)

        # Tabla de órdenes (sin columna ID, con OBSERVACIONES, editable ESTADO)
        self.ordenes_tabla = QTableWidget()
        self.ordenes_tabla.setColumnCount(5)
        self.ordenes_tabla.setHorizontalHeaderLabels([
            "Código", "Producto", "Cantidad", "Observaciones", "Estado"
        ])
        self.ordenes_tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ordenes_tabla.verticalHeader().setVisible(False)
        self.ordenes_tabla.setSelectionBehavior(QTableWidget.SelectRows)
        self.ordenes_tabla.itemChanged.connect(self.editar_celda_orden)
        main_layout.addWidget(self.ordenes_tabla)

        # Sección de materia prima y resumen de costos en horizontal
        bottom_layout = QHBoxLayout()

        # Grupo de detalle de materia prima utilizada
        detalle_group = QGroupBox("Materia Prima Utilizada")
        detalle_layout = QVBoxLayout()
        self.detalle_tabla = QTableWidget()
        self.detalle_tabla.setColumnCount(2)
        self.detalle_tabla.setHorizontalHeaderLabels([
            "Materia Prima", "Cantidad Utilizada"
        ])
        self.detalle_tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.detalle_tabla.verticalHeader().setVisible(False)
        detalle_layout.addWidget(self.detalle_tabla)
        detalle_group.setLayout(detalle_layout)
        bottom_layout.addWidget(detalle_group, 2)

        # Línea vertical separadora
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("color: #b2bec3;")
        bottom_layout.addWidget(separator)

        # Resumen de costos
        resumen_group = QGroupBox("Resumen de Costos")
        resumen_layout = QVBoxLayout()
        self.resumen_label = QLabel()
        self.resumen_label.setObjectName("ResumenCostos")
        self.resumen_label.setAlignment(Qt.AlignLeft)
        resumen_layout.addWidget(self.resumen_label)
        resumen_group.setLayout(resumen_layout)
        bottom_layout.addWidget(resumen_group, 3)

        main_layout.addLayout(bottom_layout)

        self.orden_id_seleccionada = None
        self.cargar_ordenes()

        # Selección de fila para mostrar detalle
        self.ordenes_tabla.selectionModel().selectionChanged.connect(self.on_fila_seleccionada)

    def cargar_ordenes(self):
        ordenes = self.controller.get_ordenes()
        self.ordenes_tabla.blockSignals(True)
        self.ordenes_tabla.setRowCount(0)
        for orden in ordenes:
            # orden = (id, codigo, producto, cantidad, observaciones, estado ...)
            row = self.ordenes_tabla.rowCount()
            self.ordenes_tabla.insertRow(row)
            # Código (guarda el id real en UserRole)
            codigo_item = QTableWidgetItem(str(orden[1]))
            codigo_item.setData(Qt.UserRole, orden[0])
            self.ordenes_tabla.setItem(row, 0, codigo_item)
            # Producto
            self.ordenes_tabla.setItem(row, 1, QTableWidgetItem(str(orden[2])))
            # Cantidad
            self.ordenes_tabla.setItem(row, 2, QTableWidgetItem(str(orden[3])))
            # Observaciones (editable)
            obs_item = QTableWidgetItem(str(orden[4]) if len(orden) > 4 and orden[4] is not None else "")
            obs_item.setFlags(obs_item.flags() | Qt.ItemIsEditable)
            self.ordenes_tabla.setItem(row, 3, obs_item)
            # Estado como ComboBox
            estado_combo = QComboBox()
            estados = ["PENDIENTE", "EN PROCESO", "FINALIZADA", "CANCELADA"]
            estado_actual = str(orden[5]).upper() if len(orden) > 5 else ""
            estado_combo.addItems(estados)
            if estado_actual in estados:
                estado_combo.setCurrentText(estado_actual)
            else:
                estado_combo.setCurrentIndex(0)
            # Colores según estado
            def set_estado_color(combo, estado):
                if estado == "FINALIZADA":
                    combo.setStyleSheet("QComboBox { background-color: #77c888; color: #222; }")
                elif estado == "EN PROCESO":
                    combo.setStyleSheet("QComboBox { background-color: #ffe066; color: #222; }")
                elif estado == "PENDIENTE":
                    combo.setStyleSheet("QComboBox { background-color: #ffe066; color: #222; }")
                elif estado == "CANCELADA":
                    combo.setStyleSheet("QComboBox { background-color: #dc3545; color: white; }")
                else:
                    combo.setStyleSheet("QComboBox { background-color: #dbdbdb; color: #222; }")
            set_estado_color(estado_combo, estado_actual)
            def on_estado_changed(value, combo=estado_combo, row=row):
                set_estado_color(combo, value)
                self.cambiar_estado_orden(row, value)
            estado_combo.currentTextChanged.connect(on_estado_changed)
            self.ordenes_tabla.setCellWidget(row, 4, estado_combo)
        self.ordenes_tabla.blockSignals(False)

    def on_fila_seleccionada(self, selected, deselected):
        indexes = selected.indexes()
        if indexes:
            row = indexes[0].row()
            self.mostrar_detalle_orden(row, 0)

    def cambiar_estado_orden(self, row, nuevo_estado):
        orden_id = self.ordenes_tabla.item(row, 0).data(Qt.UserRole)
        self.controller.actualizar_estado_orden(orden_id, nuevo_estado)

    def editar_celda_orden(self, item):
        row = item.row()
        col = item.column()
        orden_id = self.ordenes_tabla.item(row, 0).data(Qt.UserRole)
        if col == 3:  # Observaciones
            nueva_obs = item.text()
            self.controller.actualizar_observaciones_orden(orden_id, nueva_obs)

    def crear_orden(self):
        prod_id = self.producto_combo.currentData()
        try:
            cantidad = float(self.cantidad_input.text())
        except Exception:
            QMessageBox.warning(self, "Error", "Cantidad inválida")
            return
        if not prod_id or cantidad <= 0:
            QMessageBox.warning(self, "Error", "Seleccione producto y cantidad válida")
            return

        # Validación de stock antes de crear la orden
        faltantes = self.controller.puede_producir(prod_id, cantidad)
        if faltantes:
            mensaje = "No hay suficiente Materia prima para producir:\n"
            for f in faltantes:
                mensaje += f"- {f['nombre']} (necesaria: {f['necesaria']:.2f}, en stock: {f['en_stock']:.2f})\n"
            QMessageBox.warning(self, "Faltantes en inventario", mensaje)
            return

        orden_id = self.controller.crear_orden(prod_id, cantidad)
        if orden_id:
            QMessageBox.information(self, "Éxito", "Orden creada")
            self.cargar_ordenes()
        else:
            QMessageBox.warning(self, "Error", "No se pudo crear la orden")

    def mostrar_detalle_orden(self, row, col):
        orden_id = self.ordenes_tabla.item(row, 0).data(Qt.UserRole)
        self.orden_id_seleccionada = orden_id
        detalles = self.controller.get_detalle_orden(orden_id)
        self.detalle_tabla.setRowCount(0)

        total_mp = 0.0
        total_materia_prima = 0.0
        max_productos_posibles = float('inf')

        # Obtener cantidad producida y producto_id
        cantidad_producida = float(self.ordenes_tabla.item(row, 2).text())
        producto_nombre = self.ordenes_tabla.item(row, 1).text()
        producto_id = self.controller.get_product_id_by_name(producto_nombre)

        # Obtener volumen base
        self.controller.model.cursor.execute("SELECT volumen FROM item_especifico WHERE item_general_id = ?", (producto_id,))
        row_vol = self.controller.model.cursor.fetchone()
        volumen_base = float(row_vol[0]) if row_vol and row_vol[0] is not None else 1

        # Usar la unidad de la primera materia prima para mostrar el tipo de costo
        unidad_principal = detalles[0]['unidad'] if detalles else 'galon'

        for detalle in detalles:
            r = self.detalle_tabla.rowCount()
            self.detalle_tabla.insertRow(r)
            self.detalle_tabla.setItem(r, 0, QTableWidgetItem(str(detalle["nombre"])))
            self.detalle_tabla.setItem(r, 1, QTableWidgetItem(f"{detalle['cantidad_necesaria']:.2f} {detalle['unidad']}"))

            subtotal = float(detalle['costo_unitario']) * float(detalle['cantidad_necesaria'])
            total_mp += subtotal
            total_materia_prima += float(detalle['cantidad_necesaria'])

            # Calcular máximo de productos posibles por materia prima
            inventario_actual = self.controller.model.get_cantidad_inventario(detalle["codigo"])
            if float(detalle['cantidad_necesaria']) > 0 and cantidad_producida > 0:
                max_prod = inventario_actual / (float(detalle['cantidad_necesaria']) / cantidad_producida)
                max_productos_posibles = min(max_productos_posibles, max_prod)

        # Costo MP/Galón o MP/Kg según unidad principal
        costo_mp = total_mp / volumen_base if volumen_base else 0
        if unidad_principal.lower() == "kg":
            label_costo_mp = f"<span style='background:#ffe066; color:#222; font-weight:bold;'>&nbsp;COSTO MP/Kg: ${costo_mp:,.2f}&nbsp;</span>"
        else:
            label_costo_mp = f"<span style='background:#ffe066; color:#222; font-weight:bold;'>&nbsp;COSTO MP/Galón: ${costo_mp:,.2f}&nbsp;</span>"

        # Costos fijos
        self.controller.model.cursor.execute("""
            SELECT costo_mod, envase, etiqueta, bandeja, plastico
            FROM costos_produccion
            WHERE item_id = ?
            ORDER BY fecha_calculo DESC LIMIT 1
        """, (producto_id,))
        costos = self.controller.model.cursor.fetchone()
        costo_mod = float(costos[0]) if costos and costos[0] else 0
        envase = float(costos[1]) if costos and costos[1] else 0
        etiqueta = float(costos[2]) if costos and costos[2] else 0
        bandeja = float(costos[3]) if costos and costos[3] else 0
        plastico = float(costos[4]) if costos and costos[4] else 0

        resumen = f"""
        <table cellpadding='6' cellspacing='0' style='border-collapse:separate; border-spacing:0 4px;'>
            <tr>
                <td style='background:#ffe066; color:#222; font-weight:bold; border-radius:4px; padding:6px 16px;'>COSTO MP/Galón: ${costo_mp:,.2f}</td>
            </tr>
            <tr>
                <td style='background:#d0ebff; color:#222; font-weight:bold; border-radius:4px; padding:6px 16px;'>MOD: ${costo_mod:,.2f}</td>
            </tr>
            <tr>
                <td style='background:#ffd6e0; color:#222; font-weight:bold; border-radius:4px; padding:6px 16px;'>Envase: ${envase:,.2f}</td>
            </tr>
            <tr>
                <td style='background:#e9fac8; color:#222; font-weight:bold; border-radius:4px; padding:6px 16px;'>Etiqueta: ${etiqueta:,.2f}</td>
            </tr>
            <tr>
                <td style='background:#fff3bf; color:#222; font-weight:bold; border-radius:4px; padding:6px 16px;'>Bandeja: ${bandeja:,.2f}</td>
            </tr>
            <tr>
                <td style='background:#e7eaf6; color:#222; font-weight:bold; border-radius:4px; padding:6px 16px;'>Plástico: ${plastico:,.2f}</td>
            </tr>
            <tr>
                <td style='background:#ffe066; color:#222; font-weight:bold; border-radius:4px; padding:6px 16px;'>COSTO TOTAL PRODUCCIÓN: ${(costo_mp + costo_mod + envase + etiqueta + bandeja + plastico):,.2f}</td>
            </tr>
            <tr>
                <td style='background:#b2f2bb; color:#222; font-weight:bold; border-radius:4px; padding:6px 16px;'>PRECIO DE VENTA SUGERIDO: ${(costo_mp + costo_mod + envase + etiqueta + bandeja + plastico)*1.4:,.2f}</td>
            </tr>
            <tr>
                <td style='padding-top:12px; font-size:15px; color:#222;'>
                    TOTAL MATERIA PRIMA USADA: <b>{total_materia_prima:,.2f} {unidad_principal}</b>
                </td>
            </tr>
            <tr>
                <td style='font-size:15px; color:#222;'>
                    MAX. PRODUCTOS POSIBLES CON STOCK ACTUAL: <b>{int(max_productos_posibles) if max_productos_posibles != float('inf') else 'N/A'}</b>
                </td>
            </tr>
        </table>
        """
        self.resumen_label.setText(resumen)

    def ver_costos_orden(self):
        if not self.orden_id_seleccionada:
            QMessageBox.warning(self, "Error", "Seleccione una orden primero")
            return

        # Obtener datos de la orden
        ordenes = self.controller.get_ordenes()
        orden = None
        for o in ordenes:
            if o[0] == self.orden_id_seleccionada:
                orden = o
                break
        if not orden:
            QMessageBox.warning(self, "Error", "No se encontró la orden seleccionada")
            return

        # Obtener el id del producto
        producto_id = self.controller.get_product_id_by_name(orden[2]) if not isinstance(orden[2], int) else orden[2]
        cantidad_producida = orden[3]

        # Obtener materias primas y volumen base
        detalles = self.controller.get_detalle_orden(self.orden_id_seleccionada)
        self.controller.model.cursor.execute("SELECT volumen FROM item_especifico WHERE item_general_id = ?", (producto_id,))
        row = self.controller.model.cursor.fetchone()
        volumen_base = float(row[0]) if row and row[0] is not None else 1

        # Calcular costos de materias primas
        total_mp = 0.0
        for detalle in detalles:
            costo_unitario = detalle.get('costo_unitario', 0)
            cantidad_necesaria = detalle.get('cantidad_necesaria', 0)
            total_mp += float(costo_unitario) * float(cantidad_necesaria)

        # Costos fijos
        self.controller.model.cursor.execute("""
            SELECT costo_mod, envase, etiqueta, bandeja, plastico
            FROM costos_produccion
            WHERE item_id = ?
            ORDER BY fecha_calculo DESC LIMIT 1
        """, (producto_id,))
        costos = self.controller.model.cursor.fetchone()
        costo_mod = float(costos[0]) if costos and costos[0] else 0
        envase = float(costos[1]) if costos and costos[1] else 0
        etiqueta = float(costos[2]) if costos and costos[2] else 0
        bandeja = float(costos[3]) if costos and costos[3] else 0
        plastico = float(costos[4]) if costos and costos[4] else 0

        costo_mp = total_mp / volumen_base if volumen_base else 0
        costo_total = costo_mp + costo_mod + envase + etiqueta + bandeja + plastico
        precio_venta = costo_total * 1.4

        mensaje = (
            f"<b>COSTO MP: ${costo_mp:,.2f}</b><br>"
            f"MOD: <b>${costo_mod:,.2f}</b><br>"
            f"Envase: <b>${envase:,.2f}</b><br>"
            f"Etiqueta: <b>${etiqueta:,.2f}</b><br>"
            f"Bandeja: <b>${bandeja:,.2f}</b><br>"
            f"Plástico: <b>${plastico:,.2f}</b><br>"
            f"<hr>"
            f"<b>COSTO TOTAL PRODUCCIÓN: ${costo_total:,.2f}</b><br>"
            f"<b>PRECIO DE VENTA SUGERIDO: ${precio_venta:,.2f}</b>"
        )
        QMessageBox.information(self, "Costos de Producción", mensaje)