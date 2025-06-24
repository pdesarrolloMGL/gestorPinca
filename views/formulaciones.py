from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox, QTableWidget, QTableWidgetItem,
    QHBoxLayout, QStackedWidget, QHeaderView, QSizePolicy, QLineEdit, QPushButton, QListWidget, QListWidgetItem, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QIcon
from controllers.formulaciones_controller import FormulacionesController

def clear_layout(layout):
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget is not None:
            widget.deleteLater()
        elif item.layout() is not None:
            clear_layout(item.layout())

class Formulaciones(QWidget):
    def __init__(self):
        super().__init__()
        self.controller = FormulacionesController()

        # Widget principal de la pantalla de formulaciones
        self.pantalla_formulaciones = QWidget()
        self.pantalla_formulaciones.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        main_layout = QVBoxLayout(self.pantalla_formulaciones)
        main_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        # Título
        titulo = QLabel("Fórmulas de Producto - Consultas / Cálculos")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setObjectName("Titulo")
        main_layout.addWidget(titulo)

        # Layout horizontal para select, buscador y botones
        selector_layout = QHBoxLayout()
        selector_layout.setAlignment(Qt.AlignLeft)

        # Buscador por nombre
        self.producto_search = QLineEdit()
        self.producto_search.setPlaceholderText("Buscar producto...")
        self.producto_search.setMinimumWidth(200)
        self.producto_search.setMaximumWidth(350)
        selector_layout.addWidget(self.producto_search)

        # ComboBox para seleccionar producto
        self.producto_combo = QComboBox()
        self.producto_combo.addItem("Seleccione un producto...", None)
        self.productos = self.controller.get_productos()
        for prod_id, nombre in self.productos:
            self.producto_combo.addItem(nombre, prod_id)
        self.producto_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.producto_combo.currentIndexChanged.connect(self.mostrar_formula_producto)
        selector_layout.addWidget(self.producto_combo, stretch=1)

        # Campo para ingresar volumen personalizado
        self.volumen_input = QLineEdit()
        self.volumen_input.setPlaceholderText("Volumen: ")
        self.volumen_input.setMinimumWidth(100)
        self.volumen_input.setMaximumWidth(150)
        selector_layout.addWidget(self.volumen_input)

        # Botón para refrescar productos
        self.btn_refrescar = QPushButton("  REFRESCAR")
        self.btn_refrescar.setMinimumWidth(90)
        self.btn_refrescar.setMaximumWidth(120)
        self.btn_refrescar.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.btn_refrescar.setIcon(QIcon("assets/refresh.png"))
        self.btn_refrescar.clicked.connect(self.recargar_productos)
        selector_layout.addWidget(self.btn_refrescar)

        main_layout.addLayout(selector_layout)

        # Dropdown flotante para resultados de búsqueda (hijo de self)
        self.producto_list = QListWidget(self)
        self.producto_list.hide()

        # Conexiones para buscador
        self.producto_search.textChanged.connect(self.buscar_producto)
        self.producto_list.itemClicked.connect(self.seleccionar_producto_busqueda)

        # Tabla principal
        tabla_layout = QVBoxLayout()
        tabla_layout.setSpacing(0)
        tabla_layout.setContentsMargins(0, 0, 0, 0)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "N°", "CÓDIGO", "MATERIA PRIMA", "COSTO UNITARIO", "CANTIDAD NECESARIA", "CANTIDAD EN INVENTARIO", "TOTAL"
        ])
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        tabla_layout.addWidget(self.table)

        # Suma total de materias primas
        self.total_label = QLabel("TOTAL COSTO MATERIA PRIMA: $ 0.00")
        self.total_label.setObjectName("SumaTotalLabel")
        self.total_label.setAlignment(Qt.AlignRight)
        tabla_layout.addWidget(self.total_label)

        main_layout.addLayout(tabla_layout)

        # Datos técnicos y costos
        tablas_pequenas_layout = QHBoxLayout()
        tablas_pequenas_layout.setAlignment(Qt.AlignTop)

        # Tabla pequeña de datos técnicos
        self.datos_tecnicos_tabla = QTableWidget()
        self.datos_tecnicos_tabla.setColumnCount(2)
        self.datos_tecnicos_tabla.setRowCount(0)
        self.datos_tecnicos_tabla.setHorizontalHeaderLabels(["PARAMETRO", "PATRON"])
        self.datos_tecnicos_tabla.verticalHeader().setVisible(False)
        self.datos_tecnicos_tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.datos_tecnicos_tabla.setMaximumWidth(300)
        self.datos_tecnicos_tabla.setMinimumHeight(220)
        self.datos_tecnicos_tabla.setMaximumHeight(350)
        self.datos_tecnicos_tabla.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.datos_tecnicos_tabla.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.datos_tecnicos_tabla.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        tablas_pequenas_layout.addWidget(self.datos_tecnicos_tabla)

        # Widget para mostrar los costos y valores
        self.costos_widget = QWidget()
        self.costos_layout = QVBoxLayout(self.costos_widget)
        self.costos_layout.setAlignment(Qt.AlignTop)
        self.costos_layout.setSpacing(8)
        self.costos_layout.setContentsMargins(10, 10, 10, 10)
        tablas_pequenas_layout.addWidget(self.costos_widget, stretch=1)

        # Conexiones para mostrar la fórmula del producto
        self.volumen_input.textChanged.connect(self.mostrar_formula_producto)
        self.volumen_input.editingFinished.connect(self.mostrar_formula_producto)

        main_layout.addLayout(tablas_pequenas_layout)

        # Agrega la pantalla principal al stacked
        self.stacked = QStackedWidget(self)
        self.stacked.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.stacked.addWidget(self.pantalla_formulaciones)

        # Layout principal de Calculadora
        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(0, 0, 0, 0)
        layout_principal.setSpacing(0)
        layout_principal.addWidget(self.stacked)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.showMaximized()

        if self.producto_combo.count() > 1:
            self.producto_combo.setCurrentIndex(1)
            self.mostrar_formula_producto()

    def recargar_productos(self):
        self.productos = self.controller.get_productos()
        self.producto_combo.blockSignals(True)
        self.producto_combo.clear()
        self.producto_combo.addItem("Seleccione un producto...", None)
        for prod_id, nombre in self.productos:
            self.producto_combo.addItem(nombre, prod_id)
        self.producto_combo.blockSignals(False)
        if self.producto_combo.count() > 1:
            self.producto_combo.setCurrentIndex(self.producto_combo.count() - 1)
            self.mostrar_formula_producto()

    def buscar_producto(self, texto):
        self.producto_list.clear()
        if not texto:
            self.producto_list.hide()
            return
        max_width = self.producto_search.width()
        fm = self.producto_list.fontMetrics()
        for prod_id, nombre in self.productos:
            if texto.lower() in nombre.lower():
                item = QListWidgetItem(nombre)
                item.setData(Qt.UserRole, prod_id)
                self.producto_list.addItem(item)
                item_width = fm.width(nombre) + 20  # 20px de margen/padding
                if item_width > max_width:
                    max_width = item_width
        if self.producto_list.count() > 0:
            pos = self.producto_search.mapTo(self, self.producto_search.rect().bottomLeft())
            self.producto_list.move(pos)
            self.producto_list.setFixedWidth(max_width)
            self.producto_list.setMinimumHeight(300)
            self.producto_list.setMaximumHeight(500)
            self.producto_list.raise_()
            self.producto_list.show()
        else:
            self.producto_list.hide()

    def seleccionar_producto_busqueda(self, item):
        prod_id = item.data(Qt.UserRole)
        index = self.producto_combo.findData(prod_id)
        if index != -1:
            self.producto_combo.setCurrentIndex(index)
        self.producto_list.hide()
        self.producto_search.clear()

    def mostrar_formula_producto(self):
        prod_id = self.producto_combo.currentData()
        volumen_original = self.controller.get_volumen_original(prod_id) if prod_id else None
        texto_vol = self.volumen_input.text().replace(",", ".").strip()
        try:
            volumen_personalizado = float(texto_vol) if texto_vol else None
        except Exception:
            volumen_personalizado = None

        self.datos_tecnicos_tabla.setRowCount(0)
        if prod_id:
            datos = self.controller.get_datos_tecnicos(prod_id)
            nombres = [
                "VISCOSIDAD", "P / G", "COLOR", "BRILLO 60°", "SECADO",
                "CUBRIMIENTO", "MOLIENDA", "PH", "PODER TINTOREO"
            ]
            if datos:
                for i, valor in enumerate(datos):
                    mostrar = str(valor) if valor not in (None, '', 'None') else "N/A"
                    self.datos_tecnicos_tabla.insertRow(self.datos_tecnicos_tabla.rowCount())
                    row = self.datos_tecnicos_tabla.rowCount() - 1

                    item_param = QTableWidgetItem(nombres[i])
                    item_param.setBackground(QColor("white"))
                    self.datos_tecnicos_tabla.setItem(row, 0, item_param)

                    item_valor = QTableWidgetItem(mostrar)
                    item_valor.setBackground(QColor("white"))
                    self.datos_tecnicos_tabla.setItem(row, 1, item_valor)

        clear_layout(self.costos_layout)

        if prod_id is None:
            self.table.setHorizontalHeaderLabels([""] * self.table.columnCount())
            self.table.setRowCount(1)
            for col in range(self.table.columnCount()):
                self.table.setItem(0, col, QTableWidgetItem(""))
            self.total_label.setText("TOTAL COSTO MATERIA PRIMA: $ 0.00")
            return
        else:
            self.table.setHorizontalHeaderLabels([
                "N°", "CÓDIGO", "MATERIA PRIMA", "COSTO UNITARIO", "CANTIDAD NECESARIA", "CANTIDAD EN INVENTARIO", "TOTAL"
            ])

        materias = self.controller.get_materias_primas(prod_id)
        factor_volumen = 1.0
        if volumen_original and volumen_personalizado:
            factor_volumen = volumen_personalizado / volumen_original

        self.table.setRowCount(0)
        self.table.clearContents()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "N°", "CÓDIGO", "MATERIA PRIMA", "COSTO UNITARIO", "CANTIDAD NECESARIA", "CANTIDAD EN INVENTARIO", "TOTAL"
        ])
        self.table.verticalHeader().setVisible(False)
        self.table.setRowCount(len(materias))
        suma_total = 0.0
        suma_cantidades = 0.0  # <-- suma de cantidades ajustadas

        for i, (codigo, nombre, costo_unitario, cantidad, unidad) in enumerate(materias):
            cantidad_ajustada = float(cantidad) * factor_volumen

            item_n = QTableWidgetItem(str(i + 1))
            item_n.setTextAlignment(Qt.AlignCenter)
            item_n.setBackground(QColor("white"))
            self.table.setItem(i, 0, item_n)

            item_codigo = QTableWidgetItem(str(codigo))
            item_codigo.setTextAlignment(Qt.AlignCenter)
            item_codigo.setBackground(QColor("white"))
            self.table.setItem(i, 1, item_codigo)

            item_nombre = QTableWidgetItem(str(nombre))
            item_nombre.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
            item_nombre.setBackground(QColor("white"))
            self.table.setItem(i, 2, item_nombre)

            try:
                costo_unitario_fmt = "$ {:,.2f}".format(float(costo_unitario))
            except Exception:
                costo_unitario_fmt = str(costo_unitario)
            item_costo = QTableWidgetItem("   " + costo_unitario_fmt)
            item_costo.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
            item_costo.setBackground(QColor("white"))
            self.table.setItem(i, 3, item_costo)

            item_cant = QTableWidgetItem("{:,.2f}".format(cantidad_ajustada))
            item_cant.setTextAlignment(Qt.AlignCenter)
            item_cant.setBackground(QColor("white"))
            self.table.setItem(i, 4, item_cant)

            cantidad_inventario = self.controller.get_cantidad_inventario(codigo)
            item_inv = QTableWidgetItem("{:,.2f}".format(cantidad_inventario))
            item_inv.setTextAlignment(Qt.AlignCenter)
            item_inv.setBackground(QColor("white"))
            if cantidad_inventario >= cantidad_ajustada:
                item_inv.setBackground(QColor(204, 255, 204))  # Verde pastel suave
            else:
                item_inv.setBackground(QColor(255, 204, 204))  # Rojo pastel suave
            self.table.setItem(i, 5, item_inv)

            try:
                total = float(costo_unitario) * cantidad_ajustada
            except Exception:
                total = 0.0
            try:
                total_fmt = "$ {:,.2f}".format(float(total))
            except Exception:
                total_fmt = str(total)
            item_total = QTableWidgetItem("   " + total_fmt)
            item_total.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
            item_total.setBackground(QColor("white"))
            self.table.setItem(i, 6, item_total)

            try:
                suma_total += float(total)
                suma_cantidades += float(cantidad_ajustada)  # <-- suma cantidades
            except Exception:
                pass

        # Muestra ambos totales en el label
        self.total_label.setText(
            f"TOTAL CANTIDAD: {suma_cantidades:,.2f}  |  TOTAL COSTO MATERIA PRIMA: $ {suma_total:,.2f}   "
        )

        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)  # N°
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)  # CÓDIGO
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch) # MATERIA PRIMA
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch) # COSTO UNITARIO
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents) # CANTIDAD
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents) # EN INVENTARIO
        self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.Stretch) # TOTAL

        # --- COSTOS Y SUMA AJUSTADA --- #
        costos = self.controller.get_costos_fijos(prod_id)
        costo_mod = float(costos[2]) if costos and self.es_numero(costos[2]) else 0
        envase = float(costos[3]) if costos and self.es_numero(costos[3]) else 0
        etiqueta = float(costos[4]) if costos and self.es_numero(costos[4]) else 0
        bandeja = float(costos[5]) if costos and self.es_numero(costos[5]) else 0
        plastico = float(costos[6]) if costos and self.es_numero(costos[6]) else 0

        if volumen_original and volumen_original > 0:
            costo_mp_galon = suma_total / volumen_original
        else:
            costo_mp_galon = 0

        costo_total = costo_mp_galon + costo_mod + envase + etiqueta + bandeja + plastico
        precio_venta = costo_total * 1.4 if costo_total else 0

        fila1 = QHBoxLayout()
        fila2 = QHBoxLayout()
        fila1.setSpacing(20)
        fila2.setSpacing(20)

        nombre_producto = None
        for pid, n in self.productos:
            if pid == prod_id:
                nombre_producto = n
                break

        if nombre_producto and "PASTA" in nombre_producto.upper():
            texto_costo_mp = f"COSTO MP/Kg: <b>{f'$ {costo_mp_galon:,.2f}' if self.es_numero(costo_mp_galon) else 'N/A'}</b>"
        else:
            texto_costo_mp = f"COSTO MP/Galon: <b>{f'$ {costo_mp_galon:,.2f}' if self.es_numero(costo_mp_galon) else 'N/A'}</b>"

        label_mp = QLabel(texto_costo_mp)
        label_mp.setObjectName("CostoMPLabel")
        fila1.addWidget(label_mp)

        label_mod = QLabel(f"COSTO MOD: {f'$ {costo_mod:,.2f}' if self.es_numero(costo_mod) else 'N/A'}")
        label_mod.setObjectName("CostoMODLabel")
        label_env = QLabel(f"ENVASE: {f'$ {envase:,.2f}' if self.es_numero(envase) else 'N/A'}")
        label_env.setObjectName("EnvaseLabel")
        label_eti = QLabel(f"ETIQUETA: {f'$ {etiqueta:,.2f}' if self.es_numero(etiqueta) else 'N/A'}")
        label_eti.setObjectName("EtiquetaLabel")
        label_ban = QLabel(f"BANDEJA: {f'$ {bandeja:,.2f}' if self.es_numero(bandeja) else 'N/A'}")
        label_ban.setObjectName("BandejaLabel")
        label_pla = QLabel(f"PLASTICO: {f'$ {plastico:,.2f}' if self.es_numero(plastico) else 'N/A'}")
        label_pla.setObjectName("PlasticoLabel")

        fila1.addWidget(label_mod)
        fila1.addWidget(label_env)
        fila1.addWidget(label_eti)
        fila2.addWidget(label_ban)
        fila2.addWidget(label_pla)

        label_total = QLabel(f"COSTO TOTAL: <b>{f'$ {costo_total:,.2f}' if self.es_numero(costo_total) else 'N/A'}</b>")
        label_total.setObjectName("CostoTotalLabel")
        label_precio = QLabel(f"PRECIO VENTA: <b>{f'$ {precio_venta:,.2f}' if self.es_numero(precio_venta) else 'N/A'}</b>")
        label_precio.setObjectName("PrecioVentaLabel")
        fila2.addWidget(label_total)
        fila2.addWidget(label_precio)

        self.costos_layout.addLayout(fila1)
        self.costos_layout.addLayout(fila2)

    def es_producto_por_kg(self, prod_id):
        nombre = None
        for pid, n in self.productos:
            if pid == prod_id:
                nombre = n
                break
        if nombre and "PASTA" not in nombre.upper():
            return False  # Por defecto, galón
        return True

    def es_numero(self, valor):
        try:
            float(valor)
            return True
        except (TypeError, ValueError):
            return False

    def mostrar_costos_orden(self, orden_id):
        # 1. Obtener datos de la orden
        orden = None
        for o in self.controller.get_ordenes():
            if (isinstance(o, dict) and o['id'] == orden_id) or (isinstance(o, tuple) and o[0] == orden_id):
                orden = o
                break
        if not orden:
            QMessageBox.warning(self, "Error", "No se encontró la orden seleccionada")
            return

        # 2. Obtener producto y cantidad producida
        producto_id = orden['id'] if isinstance(orden, dict) else orden[0]
        cantidad_producida = orden['cantidad_producida'] if isinstance(orden, dict) else orden[3]

        # 3. Obtener formulación y volumen base
        materias = self.controller.model.puede_producir(producto_id, cantidad_producida, solo_materias=True)
        self.controller.model.cursor.execute("SELECT volumen FROM item_especifico WHERE item_general_id = ?", (producto_id,))
        row = self.controller.model.cursor.fetchone()
        volumen_base = float(row[0]) if row and row[0] is not None else 1

        # 4. Calcular costos de materias primas
        total_mp = 0.0
        for mp in materias:
            # mp debe tener: id, codigo, nombre, cantidad_base, unidad, costo_unitario
            costo_unitario = mp.get('costo_unitario', 0) if isinstance(mp, dict) else (mp[5] if len(mp) > 5 else 0)
            cantidad_base = mp.get('cantidad', 0) if isinstance(mp, dict) else mp[3]
            cantidad_necesaria = float(cantidad_base) * (cantidad_producida / volumen_base)
            total_mp += float(costo_unitario) * cantidad_necesaria

        # 5. Obtener costos fijos
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

        # 6. Calcular costo total
        costo_total = total_mp + costo_mod + envase + etiqueta + bandeja + plastico

        # 7. Mostrar en un QMessageBox (puedes adaptarlo a un QLabel o layout)
        mensaje = (
            f"<b>COSTOS DE LA ORDEN</b><br>"
            f"Materia Prima: <b>${total_mp:,.2f}</b><br>"
            f"MOD: <b>${costo_mod:,.2f}</b><br>"
            f"Envase: <b>${envase:,.2f}</b><br>"
            f"Etiqueta: <b>${etiqueta:,.2f}</b><br>"
            f"Bandeja: <b>${bandeja:,.2f}</b><br>"
            f"Plástico: <b>${plastico:,.2f}</b><br>"
            f"<hr>"
            f"<b>COSTO TOTAL PRODUCCIÓN: ${costo_total:,.2f}</b>"
        )
        QMessageBox.information(self, "Costos de Producción", mensaje)