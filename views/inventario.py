from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QMessageBox, QHBoxLayout, QSizePolicy, QLabel, QLineEdit,
    QDialog, QComboBox, QFormLayout, QSpinBox, QStackedWidget, QHeaderView
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from data.connection import get_connection
from views.produccion import Produccion

class Inventario(QWidget):
    def __init__(self):
        super().__init__()

        self.stacked = QStackedWidget(self)

        # ----------- Pantalla de Inventario -----------
        self.pantalla_inventario = QWidget()
        main_layout = QVBoxLayout(self.pantalla_inventario)
        main_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        # Título dinámico
        self.titulo_label = QLabel("Inventario de Productos")
        self.titulo_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.titulo_label)

        # Buscador
        buscador_layout = QHBoxLayout()
        buscador_layout.setAlignment(Qt.AlignCenter)
        self.buscador = QLineEdit()
        self.buscador.setObjectName("BuscadorInventario")
        self.buscador.setPlaceholderText("Buscar por nombre, código o tipo...")
        self.buscador.textChanged.connect(self.buscar)
        btn_buscar = QPushButton("Buscar")
        btn_buscar.setObjectName("BtnBuscarInventario")
        btn_buscar.clicked.connect(self.buscar)
        buscador_layout.addWidget(self.buscador)
        buscador_layout.addWidget(btn_buscar)
        main_layout.addLayout(buscador_layout)

        # Botones para elegir la tabla
        botones_tabla_layout = QHBoxLayout()
        botones_tabla_layout.setAlignment(Qt.AlignCenter)

        self.btn_productos = QPushButton("Productos")
        self.btn_productos.setObjectName("btnInventario")
        self.btn_productos.clicked.connect(self.mostrar_productos)
        botones_tabla_layout.addWidget(self.btn_productos)
        
        self.btn_materia = QPushButton("Materia Prima")
        self.btn_materia.setObjectName("btnInventario")
        self.btn_materia.clicked.connect(self.mostrar_materia_prima)
        botones_tabla_layout.addWidget(self.btn_materia)

        # Botón para agregar
        self.btn_agregar = QPushButton("Agregar producto")
        self.btn_agregar.setObjectName("btnAgregarInventario")
        self.btn_agregar.clicked.connect(self.abrir_agregar)
        botones_tabla_layout.addWidget(self.btn_agregar)

        main_layout.addLayout(botones_tabla_layout)

        # Tabla en contenedor centrado
        self.table = QTableWidget()
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table.verticalHeader().setVisible(False)
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.table.setMinimumHeight(300)
        self.table.setMinimumWidth(600)
        self.table.setMaximumHeight(16777215)
        self.table.setMaximumWidth(16777215)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        tabla_contenedor = QHBoxLayout()
        tabla_contenedor.setAlignment(Qt.AlignHCenter)
        tabla_contenedor.addWidget(self.table)
        main_layout.addLayout(tabla_contenedor)

        # ----------- Fin pantalla de Inventario -----------

        self.stacked.addWidget(self.pantalla_inventario)

        # Layout principal de Inventario
        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(0, 0, 0, 0)
        layout_principal.setSpacing(0)
        layout_principal.addWidget(self.stacked)

        self.pantalla_produccion = None

        # Conexión a la base de datos
        self.conn = get_connection()
        self.cursor = self.conn.cursor()

        # Estado para saber qué tabla mostrar
        self.tabla_actual = "productos"

        # Mostrar productos al iniciar
        self.mostrar_productos()

    def actualizar_boton_activo(self):
        self.btn_productos.setProperty("class", "")
        self.btn_materia.setProperty("class", "")
        if self.tabla_actual == "productos":
            self.btn_productos.setProperty("class", "active-inventario")
        else:
            self.btn_materia.setProperty("class", "active-inventario")
        self.btn_productos.style().unpolish(self.btn_productos)
        self.btn_productos.style().polish(self.btn_productos)
        self.btn_materia.style().unpolish(self.btn_materia)
        self.btn_materia.style().polish(self.btn_materia)
        
    def ajustar_tabla_al_contenido(self):
        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()
        for i in range(self.table.columnCount()):
            header_text = self.table.horizontalHeaderItem(i).text().lower()
            if header_text == "nombre":
                self.table.setColumnWidth(i, 350)
            elif header_text == "tipo":
                self.table.setColumnWidth(i, 150)
        ancho_total = sum([self.table.columnWidth(i) for i in range(self.table.columnCount())])
        self.table.setMinimumWidth(ancho_total)
        self.table.setMaximumWidth(16777215)
        self.table.setMaximumHeight(16777215)

    def buscar(self):
        texto = self.buscador.text().strip().lower()
        if self.tabla_actual == "productos":
            self.mostrar_productos(filtro=texto)
        else:
            self.mostrar_materia_prima(filtro=texto)

    def abrir_agregar(self):
        if self.tabla_actual == "productos":
            self.abrir_formulario_producto()
        else:
            self.abrir_modal_materia_prima()

    def abrir_formulario_producto(self):
        if not self.pantalla_produccion:
            self.pantalla_produccion = Produccion(parent=self)
            btn_volver = QPushButton("Volver")
            btn_volver.setObjectName("btnVolverProduccion")
            btn_volver.clicked.connect(self.volver_a_inventario)
            self.pantalla_produccion.layout().addWidget(btn_volver)
            self.stacked.addWidget(self.pantalla_produccion)
        self.stacked.setCurrentWidget(self.pantalla_produccion)
    
    def volver_a_inventario(self):
        self.stacked.setCurrentWidget(self.pantalla_inventario)

    def abrir_modal_materia_prima(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Opciones de Materia Prima")
        layout = QVBoxLayout(dialog)
        btn_nueva = QPushButton("Agregar materia prima nueva")
        btn_stock = QPushButton("Agregar stock a materia prima existente")
        layout.addWidget(btn_nueva)
        layout.addWidget(btn_stock)
        dialog.setLayout(layout)

        btn_nueva.clicked.connect(lambda: [dialog.accept(), self.abrir_formulario_materia_prima()])
        btn_stock.clicked.connect(lambda: [dialog.accept(), self.abrir_formulario_sumar_stock()])
        dialog.exec_()

    def abrir_formulario_materia_prima(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Nueva Materia Prima")
        form_layout = QFormLayout(dialog)
        codigo = QLineEdit()
        nombre = QLineEdit()
        costo = QLineEdit()
        cantidad = QSpinBox()
        cantidad.setMaximum(1000000)
        # unidad = QComboBox()  # Eliminado
        # unidad.addItems(["KILO", "LITRO"])  # Eliminado
        form_layout.addRow("Código:", codigo)
        form_layout.addRow("Nombre:", nombre)
        form_layout.addRow("Costo unitario:", costo)
        form_layout.addRow("Cantidad:", cantidad)
        # form_layout.addRow("Unidad:", unidad)  # Eliminado
        btn_guardar = QPushButton("Guardar")
        form_layout.addRow(btn_guardar)
        dialog.setLayout(form_layout)

        def guardar():
            try:
                self.cursor.execute(
                    "INSERT INTO materia_prima (codigo, nombre, costo_unitario, cantidad) VALUES (?, ?, ?, ?)",
                    (codigo.text(), nombre.text(), float(costo.text()), cantidad.value())
                )
                self.conn.commit()
                QMessageBox.information(self, "Éxito", "Materia prima agregada correctamente.")
                dialog.accept()
                self.mostrar_materia_prima()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

        btn_guardar.clicked.connect(guardar)
        dialog.exec_()

    def abrir_formulario_sumar_stock(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Agregar stock a materia prima")
        form_layout = QFormLayout(dialog)
        self.cursor.execute("SELECT id, nombre FROM materia_prima")
        items = self.cursor.fetchall()
        select = QComboBox()
        for id_, nombre in items:
            select.addItem(nombre, id_)
        cantidad = QSpinBox()
        cantidad.setMaximum(1000000)
        form_layout.addRow("Materia prima:", select)
        form_layout.addRow("Cantidad a agregar:", cantidad)
        btn_sumar = QPushButton("Sumar")
        form_layout.addRow(btn_sumar)
        dialog.setLayout(form_layout)

        def sumar():
            id_mp = select.currentData()
            cant = cantidad.value()
            self.cursor.execute("UPDATE materia_prima SET cantidad = cantidad + ? WHERE id = ?", (cant, id_mp))
            self.conn.commit()
            QMessageBox.information(self, "Éxito", "Cantidad sumada correctamente.")
            dialog.accept()
            self.mostrar_materia_prima()

        btn_sumar.clicked.connect(sumar)
        dialog.exec_()
    
    def eliminar_fila_por_boton(self, row, tabla):
        # Obtiene el código del producto/materia prima de la fila
        codigo_item = self.table.item(row, 1)  # Columna 1 = CODIGO
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
            if tabla == "productos":
                self.cursor.execute("DELETE FROM productos WHERE codigo = ?", (codigo,))
                self.conn.commit()
                self.mostrar_productos()
            elif tabla == "materia_prima":
                self.cursor.execute("DELETE FROM materia_prima WHERE codigo = ?", (codigo,))
                self.conn.commit()
                self.mostrar_materia_prima()

    def mostrar_productos(self, filtro=None):
        self.tabla_actual = "productos"
        self.actualizar_boton_activo()
        self.titulo_label.setText("Inventario de Productos")
        self.btn_agregar.setText("Agregar producto")
        self.cursor.execute("PRAGMA table_info(productos)")
        columnas_db = [col[1] for col in self.cursor.fetchall()]
        columnas_esperadas = ["codigo", "nombre", "costo_unitario", "tipo", "cantidad"]
        for col in columnas_esperadas:
            if col not in columnas_db:
                QMessageBox.critical(self, "Error", f"La columna '{col}' no existe en la tabla productos.")
                return

        query = "SELECT codigo, nombre, costo_unitario, tipo, cantidad FROM productos"
        params = ()
        if filtro:
            query += " WHERE lower(codigo) LIKE ? OR lower(nombre) LIKE ? OR lower(tipo) LIKE ?"
            params = (f"%{filtro}%", f"%{filtro}%", f"%{filtro}%")
        self.cursor.execute(query, params)
        resultados = self.cursor.fetchall()
        columnas = ["N°", "CODIGO", "NOMBRE", "COSTO UNITARIO", "TIPO", "CANTIDAD", "ELIMINAR"]

        for i in range(self.table.rowCount()):
            for j in range(self.table.columnCount()):
                widget = self.table.cellWidget(i, j)
                if widget is not None:
                    self.table.removeCellWidget(i, j)

        self.table.setRowCount(len(resultados))
        self.table.setColumnCount(len(columnas))
        self.table.setHorizontalHeaderLabels(columnas)

        for i, fila in enumerate(resultados):
            self.table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
            for j, valor in enumerate(fila):
                header_text = self.table.horizontalHeaderItem(j + 1).text().lower()
                item = QTableWidgetItem(str(valor))
                # Centra todo menos la columna "nombre"
                if header_text != "nombre":
                    item.setTextAlignment(Qt.AlignCenter)
                if header_text == "costo unitario":
                    try:
                        valor = float(valor)
                        item.setText("$ {:,.2f}".format(valor))
                    except Exception:
                        pass
                self.table.setItem(i, j + 1, item)
            btn = QPushButton()
            btn.setIcon(QIcon("assets/trash.png"))
            btn.setObjectName("btnEliminar")
            btn.setToolTip("Eliminar fila")
            btn.clicked.connect(lambda _, row=i: self.eliminar_fila_por_boton(row, "productos"))
            self.table.setCellWidget(i, len(columnas) - 1, btn)

        self.ajustar_tabla_al_contenido()

    def mostrar_materia_prima(self, filtro=None):
        self.tabla_actual = "materia_prima"
        self.actualizar_boton_activo()
        self.titulo_label.setText("Inventario de Materia Prima")
        self.btn_agregar.setText("Agregar materia prima")
        self.cursor.execute("PRAGMA table_info(materia_prima)")
        columnas_db = [col[1] for col in self.cursor.fetchall()]
        columnas_esperadas = ["codigo", "nombre", "costo_unitario", "cantidad"]
        for col in columnas_esperadas:
            if col not in columnas_db:
                QMessageBox.critical(self, "Error", f"La columna '{col}' no existe en la tabla materia_prima.")
                return

        query = "SELECT codigo, nombre, costo_unitario, cantidad FROM materia_prima WHERE nombre IS NOT NULL AND nombre != ''"
        params = ()
        if filtro:
            query += " AND (lower(codigo) LIKE ? OR lower(nombre) LIKE ?)"
            params = (f"%{filtro}%", f"%{filtro}%")
        self.cursor.execute(query, params)
        resultados = self.cursor.fetchall()
        columnas = ["N°", "CODIGO", "NOMBRE", "COSTO UNITARIO", "CANTIDAD", "ELIMINAR"]
        self.table.setRowCount(len(resultados))
        self.table.setColumnCount(len(columnas))
        self.table.setHorizontalHeaderLabels(columnas)

        for i in range(self.table.rowCount()):
            for j in range(self.table.columnCount()):
                widget = self.table.cellWidget(i, j)
                if widget is not None:
                    self.table.removeCellWidget(i, j)

        for i, fila in enumerate(resultados):
            self.table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
            for j, valor in enumerate(fila):
                header_text = self.table.horizontalHeaderItem(j + 1).text().lower()
                item = QTableWidgetItem(str(valor))
                # Centra todo menos la columna "nombre"
                if header_text != "nombre":
                    item.setTextAlignment(Qt.AlignCenter)
                if header_text == "costo unitario":
                    try:
                        valor = float(valor)
                        item.setText("$ {:,.2f}".format(valor))
                    except Exception:
                        pass
                self.table.setItem(i, j + 1, item)
            btn = QPushButton()
            btn.setIcon(QIcon("assets/trash.png"))
            btn.setObjectName("btnEliminar")
            btn.setToolTip("Eliminar fila")
            btn.clicked.connect(lambda _, row=i: self.eliminar_fila_por_boton(row, "materia_prima"))
            self.table.setCellWidget(i, len(columnas) - 1, btn)

        self.ajustar_tabla_al_contenido()