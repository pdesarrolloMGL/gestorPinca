from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox, QTableWidget, QTableWidgetItem,
    QHBoxLayout, QStackedWidget, QHeaderView, QSizePolicy, QLineEdit, QPushButton
)
from PyQt5.QtCore import Qt
from controllers.formulaciones_controller import FormulacionesController

class Formulaciones(QWidget):
    def __init__(self):
        super().__init__()
        self.controller = FormulacionesController()

        # StackedWidget para alternar entre pantallas
        self.stacked = QStackedWidget(self)

        # Pantalla principal (formulaciones)
        self.pantalla_formulaciones = QWidget()
        main_layout = QVBoxLayout(self.pantalla_formulaciones)
        main_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        # Título
        titulo = QLabel("Consulta de Fórmula de Producto")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setObjectName("Titulo")
        main_layout.addWidget(titulo)

        # Layout horizontal para select y botón
        selector_layout = QHBoxLayout()
        selector_layout.setAlignment(Qt.AlignCenter)

        # ComboBox para seleccionar producto
        self.producto_combo = QComboBox()
        self.producto_combo.addItem("Seleccione un producto...", None)
        self.productos = self.controller.get_productos()
        for prod_id, nombre in self.productos:
            self.producto_combo.addItem(nombre, prod_id)
        self.producto_combo.currentIndexChanged.connect(self.mostrar_formula_producto)
        selector_layout.addWidget(self.producto_combo)

        # Campo para ingresar volumen personalizado
        self.volumen_input = QLineEdit()
        self.volumen_input.setPlaceholderText("Volumen personalizado")
        self.volumen_input.setFixedWidth(150)
        selector_layout.addWidget(self.volumen_input)

        # Botón para recalcular con volumen personalizado
        self.btn_recalcular = QPushButton("Recalcular")
        self.btn_recalcular.clicked.connect(self.mostrar_formula_producto)
        selector_layout.addWidget(self.btn_recalcular)

        main_layout.addLayout(selector_layout)

        # Tabla principal
        tabla_layout = QVBoxLayout()
        tabla_layout.setSpacing(0)
        tabla_layout.setContentsMargins(0, 0, 0, 0)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "N°", "CÓDIGO", "MATERIA PRIMA", "COSTO UNITARIO", "CANTIDAD", "TOTAL"
        ])
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
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

        main_layout.addLayout(tablas_pequenas_layout)

        # Agrega la pantalla principal al stacked
        self.stacked.addWidget(self.pantalla_formulaciones)

        # Layout principal de Calculadora
        layout_principal = QVBoxLayout(self)
        layout_principal.addWidget(self.stacked)

        self.showMaximized()

    def mostrar_formula_producto(self):
        prod_id = self.producto_combo.currentData()

        # Obtener volumen original del producto
        volumen_original = self.controller.get_volumen_original(prod_id) if prod_id else None

        # Volumen personalizado (si el usuario lo ingresa)
        volumen_personalizado = self.volumen_input.text().replace(",", ".")
        try:
            volumen_personalizado = float(volumen_personalizado) if volumen_personalizado else None
        except Exception:
            volumen_personalizado = None

        # Mostrar datos técnicos del producto
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
                    self.datos_tecnicos_tabla.setItem(self.datos_tecnicos_tabla.rowCount()-1, 0, QTableWidgetItem(nombres[i]))
                    self.datos_tecnicos_tabla.setItem(self.datos_tecnicos_tabla.rowCount()-1, 1, QTableWidgetItem(mostrar))

        # Limpiar el widget de costos
        for i in reversed(range(self.costos_layout.count())):
            widget = self.costos_layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)

        if prod_id is None:
            self.table.setRowCount(0)
            self.table.clearContents()
            self.total_label.setText("TOTAL COSTO MATERIA PRIMA: $ 0.00")
            return

        # Obtener materias primas asociadas al producto
        materias = self.controller.get_materias_primas(prod_id)

        # Si hay volumen personalizado, recalcula cantidades
        factor_volumen = 1.0
        if volumen_original and volumen_personalizado:
            factor_volumen = volumen_personalizado / volumen_original

        self.table.setRowCount(0)
        self.table.clearContents()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "N°", "CÓDIGO", "MATERIA PRIMA", "COSTO UNITARIO", "CANTIDAD", "TOTAL"
        ])
        self.table.verticalHeader().setVisible(False)
        self.table.setRowCount(len(materias))
        suma_total = 0.0
        for i, (codigo, nombre, costo_unitario, cantidad) in enumerate(materias):
            cantidad_ajustada = float(cantidad) * factor_volumen
            self.table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
            self.table.setItem(i, 1, QTableWidgetItem(str(codigo)))
            self.table.setItem(i, 2, QTableWidgetItem(str(nombre)))
            # Formato moneda para costo unitario
            try:
                costo_unitario_fmt = "$ {:,.2f}".format(float(costo_unitario))
            except Exception:
                costo_unitario_fmt = str(costo_unitario)
            self.table.setItem(i, 3, QTableWidgetItem(costo_unitario_fmt))
            self.table.setItem(i, 4, QTableWidgetItem("{:,.2f}".format(cantidad_ajustada)))
            # Formato moneda para total
            try:
                total = float(costo_unitario) * cantidad_ajustada
            except Exception:
                total = 0.0
            try:
                total_fmt = "$ {:,.2f}".format(float(total))
            except Exception:
                total_fmt = str(total)
            self.table.setItem(i, 5, QTableWidgetItem(total_fmt))
            try:
                suma_total += float(total)
            except Exception:
                pass

        self.total_label.setText(f"TOTAL COSTO MATERIA PRIMA: $ {suma_total:,.2f}")

        # Obtener costos fijos de costos_produccion
        costos = self.controller.get_costos_fijos(prod_id)
        costo_mp_kg = costos[0] if costos else 0
        costo_mp_galon = costos[1] if costos else 0
        costo_mod = costos[2] if costos else 0
        envase = costos[3] if costos else 0
        etiqueta = costos[4] if costos else 0
        bandeja = costos[5] if costos else 0
        plastico = costos[6] if costos else 0

        # Cálculo de costo_mp_kg o costo_mp_galon y costo_total
        costo_total = None
        precio_venta = None

        if volumen_original:
            if self.es_producto_por_kg(prod_id):
                costo_mp_kg = suma_total / (volumen_personalizado if volumen_personalizado else volumen_original)
                costo_total = (costo_mp_kg if self.es_numero(costo_mp_kg) else 0) + \
                              (float(costo_mod) if self.es_numero(costo_mod) else 0) + \
                              (float(envase) if self.es_numero(envase) else 0) + \
                              (float(etiqueta) if self.es_numero(etiqueta) else 0) + \
                              (float(bandeja) if self.es_numero(bandeja) else 0) + \
                              (float(plastico) if self.es_numero(plastico) else 0)
                precio_venta = costo_total * 1.4 if costo_total is not None else None
            else:
                costo_mp_galon = suma_total / (volumen_personalizado if volumen_personalizado else volumen_original)
                costo_total = (costo_mp_galon if self.es_numero(costo_mp_galon) else 0) + \
                              (float(costo_mod) if self.es_numero(costo_mod) else 0) + \
                              (float(envase) if self.es_numero(envase) else 0) + \
                              (float(etiqueta) if self.es_numero(etiqueta) else 0) + \
                              (float(bandeja) if self.es_numero(bandeja) else 0) + \
                              (float(plastico) if self.es_numero(plastico) else 0)
                precio_venta = costo_total * 1.4 if costo_total is not None else None

        # Agrupa los costos en dos filas para mejor visualización
        fila1 = QHBoxLayout()
        fila2 = QHBoxLayout()
        fila1.setSpacing(20)
        fila2.setSpacing(20)

        # Colores personalizados para cada tipo de costo usando setObjectName
        if self.es_producto_por_kg(prod_id):
            label_mp = QLabel(f"COSTO MP/Kg: <b>{f'$ {float(costo_mp_kg):,.2f}' if self.es_numero(costo_mp_kg) else 'N/A'}</b>")
        else:
            label_mp = QLabel(f"COSTO MP/Galon: <b>{f'$ {float(costo_mp_galon):,.2f}' if self.es_numero(costo_mp_galon) else 'N/A'}</b>")
        label_mp.setObjectName("CostoMPLabel")
        fila1.addWidget(label_mp)

        label_mod = QLabel(f"COSTO MOD: {f'$ {float(costo_mod):,.2f}' if self.es_numero(costo_mod) else 'N/A'}")
        label_mod.setObjectName("CostoMODLabel")
        label_env = QLabel(f"ENVASE: {f'$ {float(envase):,.2f}' if self.es_numero(envase) else 'N/A'}")
        label_env.setObjectName("EnvaseLabel")
        label_eti = QLabel(f"ETIQUETA: {f'$ {float(etiqueta):,.2f}' if self.es_numero(etiqueta) else 'N/A'}")
        label_eti.setObjectName("EtiquetaLabel")
        label_ban = QLabel(f"BANDEJA: {f'$ {float(bandeja):,.2f}' if self.es_numero(bandeja) else 'N/A'}")
        label_ban.setObjectName("BandejaLabel")
        label_pla = QLabel(f"PLASTICO: {f'$ {float(plastico):,.2f}' if self.es_numero(plastico) else 'N/A'}")
        label_pla.setObjectName("PlasticoLabel")

        fila1.addWidget(label_mod)
        fila1.addWidget(label_env)
        fila1.addWidget(label_eti)
        fila2.addWidget(label_ban)
        fila2.addWidget(label_pla)

        # COSTO TOTAL y PRECIO VENTA resaltados y grandes
        label_total = QLabel(f"COSTO TOTAL: <b>{f'$ {float(costo_total):,.2f}' if self.es_numero(costo_total) else 'N/A'}</b>")
        label_total.setObjectName("CostoTotalLabel")
        label_precio = QLabel(f"PRECIO VENTA: <b>{f'$ {float(precio_venta):,.2f}' if self.es_numero(precio_venta) else 'N/A'}</b>")
        label_precio.setObjectName("PrecioVentaLabel")
        fila2.addWidget(label_total)
        fila2.addWidget(label_precio)

        # Limpiar el layout antes de agregar
        for i in reversed(range(self.costos_layout.count())):
            item = self.costos_layout.itemAt(i)
            if item is not None:
                widget = item.widget()
                if widget is not None:
                    widget.setParent(None)
                else:
                    self.costos_layout.removeItem(item)

        self.costos_layout.addLayout(fila1)
        self.costos_layout.addLayout(fila2)

    def es_producto_por_kg(self, prod_id):
        # Personaliza según tu lógica de negocio
        # Ejemplo: si el nombre contiene 'KG' o es de cierto tipo
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