from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QStackedWidget, QLabel, QHBoxLayout,
    QDialog, QFormLayout, QSpinBox, QPushButton, QMessageBox, QLineEdit, QHeaderView, QComboBox, QTableWidget, QAbstractItemView,
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QBrush, QColor
from controllers.inventario_controller import InventarioController
from components.buscador import Buscador
from components.botonera_tabla import BotoneraTablas
from utils.table_utils import limpiar_celdas_widget, formatear_moneda

class Inventario(QWidget):
    producto_agregado = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.controller = InventarioController()
        self.stacked = QStackedWidget(self)
        self.pantalla_inventario = QWidget()
        main_layout = QVBoxLayout(self.pantalla_inventario)
        main_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        self.titulo_label = QLabel("Inventario de Productos")
        self.titulo_label.setAlignment(Qt.AlignCenter)
        self.titulo_label.setObjectName("tituloLabel")
        main_layout.addWidget(self.titulo_label)

        self.buscador_widget = Buscador("Buscar por nombre, código o tipo...", self.buscar)
        self.buscador_widget.setObjectName("buscadorWidget")
        if hasattr(self.buscador_widget, "input") and hasattr(self.buscador_widget.input, "textChanged"):
            self.buscador_widget.input.textChanged.connect(self.buscar)
        main_layout.addWidget(self.buscador_widget)

        self.botonera = BotoneraTablas(self.mostrar_productos, self.mostrar_materia_prima, self.abrir_agregar)
        self.botonera.setObjectName("botoneraTablas")
        main_layout.addWidget(self.botonera)

        # Botón para sumar cantidad de materia prima (solo visible para materia prima)
        self.btn_sumar_materia = QPushButton("Sumar cantidad")
        self.btn_sumar_materia.setObjectName("btnSumarMateriaPrima")
        self.btn_sumar_materia.setStyleSheet("background-color: #ffc107; color: black; border-radius: 5px; padding: 6px 18px;")
        botonera_layout = self.botonera.layout()
        botonera_layout.addWidget(self.btn_sumar_materia)
        self.btn_sumar_materia.clicked.connect(self.abrir_sumar_materia_prima)
        self.btn_sumar_materia.setVisible(False)

        self.btn_restar_materia = QPushButton("Restar cantidad")
        self.btn_restar_materia.setObjectName("btnRestarMateriaPrima")
        botonera_layout.addWidget(self.btn_restar_materia)
        self.btn_restar_materia.clicked.connect(self.abrir_restar_materia_prima)
        self.btn_restar_materia.setVisible(False)

        self.btn_agregar_producto = QPushButton("Agregar producto")
        self.btn_agregar_producto.setObjectName("btnAgregarProducto")
        self.btn_agregar_producto.setStyleSheet("background-color: #28a745; color: white; border-radius: 5px; padding: 6px 18px;")
        botonera_layout.addWidget(self.btn_agregar_producto)
        self.btn_agregar_producto.clicked.connect(self.abrir_formulario_producto)
        self.btn_agregar_producto.setVisible(True)

        self.table = QTableWidget()
        self.table.setObjectName("tablaInventario")
        self.table.setSizePolicy(self.table.sizePolicy().Expanding, self.table.sizePolicy().Expanding)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(36)
        self.table.setMinimumHeight(300)
        self.table.setMinimumWidth(600)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        tabla_contenedor = QHBoxLayout()
        tabla_contenedor.setAlignment(Qt.AlignHCenter)
        tabla_contenedor.addWidget(self.table)
        main_layout.addLayout(tabla_contenedor)

        self.stacked.addWidget(self.pantalla_inventario)
        layout_principal = QVBoxLayout(self)
        layout_principal.addWidget(self.stacked)

        self.tabla_actual = "productos"
        self.mostrar_productos()

    def buscar(self, texto):
        texto = texto.strip().lower()
        if self.tabla_actual == "productos":
            self.mostrar_productos(filtro=texto)
        else:
            self.mostrar_materia_prima(filtro=texto)

    def abrir_agregar(self):
        # Solo permite agregar materia prima
        if self.tabla_actual == "materia_prima":
            self.abrir_formulario_materia_prima()

    def abrir_formulario_materia_prima(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Nueva Materia Prima")
        dialog.setObjectName("dialogMateriaPrima")
        dialog.resize(400, 100)
        form_layout = QFormLayout(dialog)
        codigo = QLineEdit()
        codigo.setObjectName("codigoMateriaPrima")
        nombre = QLineEdit()
        nombre.setObjectName("nombreMateriaPrima")
        cantidad = QSpinBox()
        cantidad.setObjectName("cantidadMateriaPrima")
        cantidad.setMaximum(1000000)
        form_layout.addRow("Código:", codigo)
        form_layout.addRow("Nombre:", nombre)
        form_layout.addRow("Cantidad:", cantidad)
        btn_guardar = QPushButton("Guardar")
        btn_guardar.setObjectName("btnGuardarMateriaPrima")
        form_layout.addRow(btn_guardar)
        dialog.setLayout(form_layout)

        def guardar():
            try:
                self.controller.add_materia_prima(
                    codigo.text(),
                    nombre.text(),
                    cantidad.value(),
                    "MATERIA PRIMA"  # Tipo fijo
                )
                QMessageBox.information(self, "Éxito", "Materia prima agregada correctamente.")
                dialog.accept()
                self.buscador_widget.input.clear()
                self.mostrar_materia_prima()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

        btn_guardar.clicked.connect(guardar)
        dialog.exec_()

    def abrir_formulario_producto(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Nuevo Producto")

        # Layout principal vertical
        layout_final = QVBoxLayout(dialog)

        # Layout horizontal para dividir en dos columnas
        main_layout = QHBoxLayout()

        # ----------- Columna izquierda: Datos del producto -----------
        left_widget = QWidget()
        left_layout = QFormLayout(left_widget)

        # Campos generales
        nombre = QLineEdit()
        codigo = QLineEdit()
        categoria = QComboBox()
        categorias = self.controller.get_categorias()  # [(id, nombre), ...]
        for cid, nombre_cat in categorias:
            categoria.addItem(nombre_cat, cid)
        left_layout.addRow("Nombre:", nombre)
        left_layout.addRow("Código:", codigo)
        left_layout.addRow("Categoría:", categoria)

        # Datos técnicos
        viscosidad = QLineEdit()
        p_g = QLineEdit()
        color = QLineEdit()
        brillo_60 = QLineEdit()
        secado = QLineEdit()
        cubrimiento = QLineEdit()
        molienda = QLineEdit()
        ph = QLineEdit()
        poder_tintoreo = QLineEdit()
        volumen = QLineEdit()
        left_layout.addRow("Viscosidad:", viscosidad)
        left_layout.addRow("P/G:", p_g)
        left_layout.addRow("Color:", color)
        left_layout.addRow("Brillo 60°:", brillo_60)
        left_layout.addRow("Secado:", secado)
        left_layout.addRow("Cubrimiento:", cubrimiento)
        left_layout.addRow("Molienda:", molienda)
        left_layout.addRow("pH:", ph)
        left_layout.addRow("Poder Tintóreo:", poder_tintoreo)
        left_layout.addRow("Volumen:", volumen)

        # Costos de producción
        envase = QLineEdit()
        etiqueta = QLineEdit()
        bandeja = QLineEdit()
        plastico = QLineEdit()
        left_layout.addRow("Envase:", envase)
        left_layout.addRow("Etiqueta:", etiqueta)
        left_layout.addRow("Bandeja:", bandeja)
        left_layout.addRow("Plástico:", plastico)

        # ----------- Columna derecha: Materias primas -----------
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        label_mp = QLabel("Materias primas y cantidades")
        label_mp.setStyleSheet("font-weight: bold; margin-bottom: 8px;")
        right_layout.addWidget(label_mp)

        # Trae [(id, nombre), ...] para que el id sea el primer campo
        materias_primas = self.controller.model.cursor.execute(
            "SELECT id, nombre FROM item_general WHERE UPPER(tipo) = 'MATERIA PRIMA'"
        ).fetchall()

        tabla_mp = QTableWidget()
        tabla_mp.setColumnCount(3)
        tabla_mp.setHorizontalHeaderLabels(["Materia Prima", "Cantidad", "Unidad"])
        tabla_mp.setRowCount(1)
        tabla_mp.setMinimumWidth(420)
        tabla_mp.setColumnWidth(0, 220)
        tabla_mp.setColumnWidth(1, 100)
        tabla_mp.setColumnWidth(2, 80)
        tabla_mp.verticalHeader().setVisible(False)
        tabla_mp.horizontalHeader().setStretchLastSection(True)
        tabla_mp.setEditTriggers(QAbstractItemView.AllEditTriggers)
        tabla_mp.setSizeAdjustPolicy(QTableWidget.AdjustToContents)
        tabla_mp.setStyleSheet("""
            QHeaderView::section {background-color: #2c3e50; color: white; font-weight: bold;}
            QTableWidget {font-size: 13px;}
        """)

        def agregar_fila():
            row = tabla_mp.rowCount()
            tabla_mp.insertRow(row)
            combo = QComboBox()
            for mp in materias_primas:
                mp_id = mp[0]
                mp_nombre = mp[1]
                combo.addItem(mp_nombre, mp_id)
            combo.setMinimumWidth(200)
            tabla_mp.setCellWidget(row, 0, combo)
            cantidad_item = QTableWidgetItem("")
            cantidad_item.setTextAlignment(Qt.AlignCenter)
            cantidad_item.setBackground(QBrush(QColor("white")))
            cantidad_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEditable | Qt.ItemIsEnabled)
            tabla_mp.setItem(row, 1, cantidad_item)
            unidad_item = QTableWidgetItem("")
            unidad_item.setTextAlignment(Qt.AlignCenter)
            unidad_item.setBackground(QBrush(QColor("white")))
            unidad_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEditable | Qt.ItemIsEnabled)
            tabla_mp.setItem(row, 2, unidad_item)

        # Primera fila
        combo = QComboBox()
        for mp in materias_primas:
            mp_id = mp[0]
            mp_nombre = mp[1]
            combo.addItem(mp_nombre, mp_id)
        combo.setMinimumWidth(200)
        tabla_mp.setCellWidget(0, 0, combo)
        cantidad_item = QTableWidgetItem("")
        cantidad_item.setTextAlignment(Qt.AlignCenter)
        cantidad_item.setBackground(QBrush(QColor("white")))
        cantidad_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEditable | Qt.ItemIsEnabled)
        tabla_mp.setItem(0, 1, cantidad_item)
        unidad_item = QTableWidgetItem("")
        unidad_item.setTextAlignment(Qt.AlignCenter)
        unidad_item.setBackground(QBrush(QColor("white")))
        unidad_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEditable | Qt.ItemIsEnabled)
        tabla_mp.setItem(0, 2, unidad_item)

        btn_agregar_fila = QPushButton("Agregar materia prima")
        btn_agregar_fila.setStyleSheet("background-color: #28a745; color: white; border-radius: 5px; padding: 6px 18px;")
        btn_agregar_fila.clicked.connect(agregar_fila)

        right_layout.addWidget(tabla_mp)
        right_layout.addWidget(btn_agregar_fila)
        right_layout.addStretch(1)

        # ----------- Ensamblar columnas -----------
        main_layout.addWidget(left_widget)
        main_layout.addWidget(right_widget)
        main_layout.setStretch(0, 2)
        main_layout.setStretch(1, 1)

        # ----------- Botón guardar debajo de ambas columnas -----------
        bottom_layout = QHBoxLayout()
        btn_guardar = QPushButton("Guardar")
        btn_guardar.setStyleSheet("background-color: #007bff; color: white; border-radius: 5px; padding: 8px 24px; font-size: 15px;")
        bottom_layout.addStretch(1)
        bottom_layout.addWidget(btn_guardar)
        bottom_layout.addStretch(1)

        # ----------- Ensamblar todo en el layout principal -----------
        layout_final.addLayout(main_layout)
        layout_final.addLayout(bottom_layout)

        def guardar():
            print("Emitiendo señal producto_agregado")
            self.producto_agregado.emit()
            # 1. Crear item_general
            nombre_val = nombre.text()
            codigo_val = codigo.text()
            tipo = "PRODUCTO"
            categoria_id = categoria.currentData()
            item_general_id = self.controller.crear_item_general(nombre_val, codigo_val, tipo)

            # 2. Crear item_especifico
            self.controller.crear_item_especifico(
                item_general_id,
                viscosidad.text(),
                p_g.text(),
                color.text(),
                brillo_60.text(),
                secado.text(),
                cubrimiento.text(),
                molienda.text(),
                ph.text(),
                poder_tintoreo.text(),
                volumen.text(),
                categoria_id
            )

            # 3. Crear costos_produccion
            self.controller.crear_costos_produccion(
                item_general_id,
                envase.text(),
                etiqueta.text(),
                bandeja.text(),
                plastico.text(),
                volumen.text()
            )

            # 4. Guardar formulaciones (receta) usando el id de la materia prima y unidad opcional
            for row in range(tabla_mp.rowCount()):
                combo = tabla_mp.cellWidget(row, 0)
                cantidad_item = tabla_mp.item(row, 1)
                unidad_item = tabla_mp.item(row, 2)
                if combo is not None and cantidad_item is not None and unidad_item is not None:
                    mp_id = combo.currentData()
                    try:
                        cantidad = float(cantidad_item.text())
                    except Exception:
                        cantidad = None
                    unidad = unidad_item.text().strip() if unidad_item.text() else None
                    if mp_id and cantidad:
                        self.controller.agregar_formulacion(item_general_id, mp_id, cantidad, unidad)
            QMessageBox.information(self, "Éxito", "Producto creado correctamente.")
            dialog.accept()
            self.mostrar_productos()

        btn_guardar.clicked.connect(guardar)
        dialog.exec_()

    def abrir_sumar_materia_prima(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Sumar cantidad a materia prima")
        dialog.resize(400, 100)
        form_layout = QFormLayout(dialog)

        # Combo para seleccionar materia prima existente
        materias = self.controller.get_materias_primas()
        nombres = [f"{m[1]} ({m[0]})" for m in materias]  # nombre (codigo)
        combo = QComboBox()
        combo.addItems(nombres)
        cantidad = QSpinBox()
        cantidad.setMaximum(1000000)
        cantidad.setMinimum(1)
        form_layout.addRow("Materia Prima:", combo)
        form_layout.addRow("Cantidad a sumar:", cantidad)
        btn_sumar = QPushButton("Sumar")
        btn_sumar.setStyleSheet("background-color: #17a2b8; color: white; border-radius: 5px; padding: 6px 18px;")
        form_layout.addRow(btn_sumar)
        dialog.setLayout(form_layout)

        def sumar():
            idx = combo.currentIndex()
            if idx < 0:
                QMessageBox.warning(self, "Advertencia", "Seleccione una materia prima.")
                return
            codigo = materias[idx][0]
            cantidad_sumar = cantidad.value()
            try:
                self.controller.model.cursor.execute(
                    "UPDATE inventario SET cantidad = IFNULL(cantidad,0) + ? WHERE item_id = (SELECT id FROM item_general WHERE codigo = ? AND UPPER(tipo) = 'MATERIA PRIMA')",
                    (cantidad_sumar, codigo)
                )
                self.controller.model.conn.commit()
                QMessageBox.information(self, "Éxito", "Cantidad sumada correctamente.")
                dialog.accept()
                self.mostrar_materia_prima()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

        btn_sumar.clicked.connect(sumar)
        dialog.exec_()

    def abrir_restar_materia_prima(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Restar cantidad a materia prima")
        dialog.resize(400, 100)
        form_layout = QFormLayout(dialog)

        materias = self.controller.get_materias_primas()
        nombres = [f"{m[1]} ({m[0]})" for m in materias]
        combo = QComboBox()
        combo.addItems(nombres)
        cantidad = QSpinBox()
        cantidad.setMaximum(1000000)
        cantidad.setMinimum(1)
        form_layout.addRow("Materia Prima:", combo)
        form_layout.addRow("Cantidad a restar:", cantidad)
        btn_restar = QPushButton("Restar")
        btn_restar.setStyleSheet("background-color: #e74c3c; color: white; border-radius: 5px; padding: 6px 18px;")
        form_layout.addRow(btn_restar)
        dialog.setLayout(form_layout)

        def restar():
            idx = combo.currentIndex()
            if idx < 0:
                QMessageBox.warning(self, "Advertencia", "Seleccione una materia prima.")
                return
            codigo = materias[idx][0]
            cantidad_restar = cantidad.value()
            try:
                self.controller.restar_materia_prima(codigo, cantidad_restar)
                QMessageBox.information(self, "Éxito", "Cantidad restada correctamente.")
                dialog.accept()
                self.mostrar_materia_prima()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

        btn_restar.clicked.connect(restar)
        dialog.exec_()

    def eliminar_fila_por_boton(self, row, tabla):
        codigo_item = self.table.item(row, 1)
        if not codigo_item:
            return
        codigo = codigo_item.text()
        confirm = QMessageBox.question(
            self,
            "Confirmar eliminación",
            f"¿Está seguro que desea eliminar este registro ({codigo})?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            tipo = "PRODUCTO" if tabla == "productos" else "MATERIA PRIMA"
            self.controller.delete_item(codigo, tipo)
            if tabla == "productos":
                self.mostrar_productos()
            else:
                self.mostrar_materia_prima()

    def mostrar_productos(self, filtro=None):
        self.tabla_actual = "productos"
        self.titulo_label.setText("Inventario de Productos")
        self.botonera.btn_agregar.setVisible(False)
        self.btn_sumar_materia.setVisible(False)
        self.btn_restar_materia.setVisible(False)
        self.btn_agregar_producto.setVisible(True)
        resultados = self.controller.get_productos(filtro)
        columnas = ["N°", "CODIGO", "NOMBRE", "COSTO UNITARIO", "CANTIDAD", "ELIMINAR"]
        limpiar_celdas_widget(self.table)
        self.table.setRowCount(len(resultados))
        self.table.setColumnCount(len(columnas))
        self.table.setHorizontalHeaderLabels(columnas)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        for i, fila in enumerate(resultados):
            item_n = QTableWidgetItem(str(i + 1))
            item_n.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 0, item_n)
            for j, valor in enumerate(fila):
                if columnas[j + 1] == "CANTIDAD":
                    valor = 0 if valor is None else valor
                    item = QTableWidgetItem(f"{float(valor):.2f}")
                else:
                    item = QTableWidgetItem(str(valor))
                if columnas[j + 1] != "NOMBRE":
                    item.setTextAlignment(Qt.AlignCenter)
                if columnas[j + 1] == "COSTO UNITARIO":
                    item.setText(formatear_moneda(valor))
                self.table.setItem(i, j + 1, item)
            btn = QPushButton()
            btn.setIcon(QIcon("assets/trash.png"))
            btn.setToolTip("Eliminar fila")
            btn.setObjectName("btnEliminar")
            btn.clicked.connect(lambda _, row=i: self.eliminar_fila_por_boton(row, "productos"))
            self.table.setCellWidget(i, len(columnas) - 1, btn)

    def mostrar_materia_prima(self, filtro=None):
        self.tabla_actual = "materia_prima"
        self.titulo_label.setText("Inventario de Materia Prima")
        self.botonera.btn_agregar.setText("Agregar materia prima")
        self.botonera.btn_agregar.setVisible(True)
        self.btn_sumar_materia.setVisible(True)
        self.btn_restar_materia.setVisible(True)
        self.btn_agregar_producto.setVisible(False)

        resultados = self.controller.get_materias_primas(filtro)
        columnas = ["N°", "CODIGO", "NOMBRE", "COSTO UNITARIO", "CANTIDAD", "ELIMINAR"]
        limpiar_celdas_widget(self.table)
        self.table.setRowCount(len(resultados))
        self.table.setColumnCount(len(columnas))
        self.table.setHorizontalHeaderLabels(columnas)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        for i, fila in enumerate(resultados):
            item_n = QTableWidgetItem(str(i + 1))
            item_n.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 0, item_n)
            for j, valor in enumerate(fila):
                if columnas[j + 1] == "CANTIDAD":
                    valor = 0 if valor is None else valor
                    item = QTableWidgetItem(f"{float(valor):.2f}")
                else:
                    item = QTableWidgetItem(str(valor))
                if columnas[j + 1] != "NOMBRE":
                    item.setTextAlignment(Qt.AlignCenter)
                if columnas[j + 1] == "COSTO UNITARIO":
                    item.setText(formatear_moneda(valor))
                self.table.setItem(i, j + 1, item)
            btn = QPushButton()
            btn.setIcon(QIcon("assets/trash.png"))
            btn.setToolTip("Eliminar fila")
            btn.setObjectName("btnEliminar")
            btn.clicked.connect(lambda _, row=i: self.eliminar_fila_por_boton(row, "materia_prima"))
            self.table.setCellWidget(i, len(columnas) - 1, btn)