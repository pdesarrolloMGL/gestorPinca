from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QHeaderView, QMessageBox, QHBoxLayout, QSizePolicy, QLabel, QLineEdit
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from data.connection import get_connection

class Inventario(QWidget):
    def __init__(self):
        super().__init__()

        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        # Título dinámico
        self.titulo_label = QLabel("Inventario de Productos")
        self.titulo_label.setObjectName("TituloInventario")
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
        
        btn_materia = QPushButton("Materia Prima")
        btn_materia.setObjectName("btnInventario")
        btn_materia.clicked.connect(self.mostrar_materia_prima)
        botones_tabla_layout.addWidget(btn_materia)

        btn_productos = QPushButton("Productos")
        btn_productos.setObjectName("btnInventario")
        btn_productos.clicked.connect(self.mostrar_productos)
        botones_tabla_layout.addWidget(btn_productos)

        main_layout.addLayout(botones_tabla_layout)

        # Tabla en contenedor centrado
        self.table = QTableWidget()
        self.table.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding) 
        self.table.verticalHeader().setVisible(False)
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        tabla_contenedor = QHBoxLayout()
        tabla_contenedor.setAlignment(Qt.AlignHCenter)
        tabla_contenedor.addWidget(self.table)
        main_layout.addLayout(tabla_contenedor)

        # Conexión a la base de datos
        self.conn = get_connection()
        self.cursor = self.conn.cursor()

        # Estado para saber qué tabla mostrar
        self.tabla_actual = "productos"

        # Mostrar productos al iniciar
        self.mostrar_productos()
    
    def ajustar_tabla_al_contenido(self):
        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()
        # Haz que la columna "nombre" sea más ancha
        for i in range(self.table.columnCount()):
            header_text = self.table.horizontalHeaderItem(i).text().lower()
            if header_text == "nombre":
                self.table.setColumnWidth(i, 350)
            elif header_text == "tipo":
                self.table.setColumnWidth(i, 150)
        ancho_total = sum([self.table.columnWidth(i) for i in range(self.table.columnCount())]) + 20
        self.table.setMinimumWidth(ancho_total)

    def buscar(self):
        texto = self.buscador.text().strip().lower()
        if self.tabla_actual == "productos":
            self.mostrar_productos(filtro=texto)
        else:
            self.mostrar_materia_prima(filtro=texto)

    def mostrar_productos(self, filtro=None):
        self.tabla_actual = "productos"
        self.titulo_label.setText("Inventario de Productos")
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
        columnas = [desc[0] for desc in self.cursor.description]
        columnas.append("Eliminar")
        self.table.setRowCount(len(resultados))
        self.table.setColumnCount(len(columnas))
        self.table.setHorizontalHeaderLabels(columnas)

        for i, fila in enumerate(resultados):
            for j, valor in enumerate(fila):
                header_text = self.table.horizontalHeaderItem(j).text().lower()
                if header_text == "costo_unitario":
                    try:
                        valor = float(valor)
                        valor = "$ {:,.2f}".format(valor)
                    except Exception:
                        pass
                self.table.setItem(i, j, QTableWidgetItem(str(valor)))
            # Botón de eliminar
            btn = QPushButton()
            btn.setIcon(QIcon("assets/delete.png"))
            btn.setObjectName("btnEliminar")
            btn.setToolTip("Eliminar fila")
            btn.clicked.connect(lambda _, row=i: self.eliminar_fila_por_boton(row, "productos"))
            self.table.setCellWidget(i, len(columnas)-1, btn)

        self.ajustar_tabla_al_contenido()

    def mostrar_materia_prima(self, filtro=None):
        self.tabla_actual = "materia_prima"
        self.titulo_label.setText("Inventario de Materia Prima")
        self.cursor.execute("PRAGMA table_info(materia_prima)")
        columnas_db = [col[1] for col in self.cursor.fetchall()]
        columnas_esperadas = ["codigo", "nombre", "costo_unitario", "cantidad"]
        for col in columnas_esperadas:
            if col not in columnas_db:
                QMessageBox.critical(self, "Error", f"La columna '{col}' no existe en la tabla materia_prima.")
                return

        # Solo mostrar materias primas con nombre no vacío
        query = "SELECT codigo, nombre, costo_unitario, cantidad FROM materia_prima WHERE nombre IS NOT NULL AND nombre != ''"
        params = ()
        if filtro:
            query += " AND (lower(codigo) LIKE ? OR lower(nombre) LIKE ?)"
            params = (f"%{filtro}%", f"%{filtro}%")
        self.cursor.execute(query, params)
        resultados = self.cursor.fetchall()
        columnas = [desc[0] for desc in self.cursor.description]
        columnas.append("Eliminar")
        self.table.setRowCount(len(resultados))
        self.table.setColumnCount(len(columnas))
        self.table.setHorizontalHeaderLabels(columnas)

        for i, fila in enumerate(resultados):
            for j, valor in enumerate(fila):
                header_text = self.table.horizontalHeaderItem(j).text().lower()
                if header_text == "costo_unitario":
                    try:
                        valor = float(valor)
                        valor = "$ {:,.2f}".format(valor)
                    except Exception:
                        pass
                self.table.setItem(i, j, QTableWidgetItem(str(valor)))
            # Botón de eliminar
            btn = QPushButton()
            btn.setIcon(QIcon("assets/delete.png"))
            btn.setObjectName("btnEliminar")
            btn.setToolTip("Eliminar fila")
            btn.clicked.connect(lambda _, row=i: self.eliminar_fila_por_boton(row, "materia_prima"))
            self.table.setCellWidget(i, len(columnas)-1, btn)

        self.ajustar_tabla_al_contenido()