from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox, QTableWidget, QTableWidgetItem
)
from PyQt5.QtCore import Qt
from data.connection import get_connection

class Calculadora(QWidget):
    def __init__(self):
        super().__init__()
        self.conn = get_connection()
        self.cursor = self.conn.cursor()

        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        # Título
        titulo = QLabel("Consulta de Fórmula de Producto")
        titulo.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(titulo)

        # ComboBox para seleccionar producto
        self.producto_combo = QComboBox()
        self.producto_combo.addItem("Seleccione un producto...", None)  # Opción vacía por defecto
        self.productos = self.obtener_productos()
        for prod_id, nombre in self.productos:
            self.producto_combo.addItem(nombre, prod_id)
        self.producto_combo.currentIndexChanged.connect(self.mostrar_formula_producto)
        main_layout.addWidget(self.producto_combo)

        # Tabla para mostrar materia prima usada por proceso
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Código", "Materia Prima", "Costo unitario", "Cantidad usada"])
        main_layout.addWidget(self.table)

        # No mostrar fórmula al iniciar
        # self.mostrar_formula_producto()

    def obtener_productos(self):
        self.cursor.execute("SELECT id, nombre FROM productos")
        return self.cursor.fetchall()

    def mostrar_formula_producto(self):
        prod_id = self.producto_combo.currentData()
        if prod_id is None:
            self.table.setRowCount(0)
            self.table.clearContents()
            return

        # Obtener los pasos/procesos del producto
        self.cursor.execute("""
            SELECT id, descripcion
            FROM producto_pasos
            WHERE producto_id = ?
            ORDER BY orden
        """, (prod_id,))
        pasos = self.cursor.fetchall()

        # Preparar filas para la tabla
        filas = []
        for paso_id, descripcion in pasos:
            # Agrega una fila para el nombre del proceso/paso (en negrita)
            filas.append((None, f"--- {descripcion} ---", None, None))
            # Materias primas de este paso
            self.cursor.execute("""
                SELECT mp.codigo, mp.nombre, mp.costo_unitario, pmp.cantidad
                FROM paso_materia_prima pmp
                JOIN materia_prima mp ON pmp.materia_prima_id = mp.id
                WHERE pmp.paso_id = ?
            """, (paso_id,))
            materias = self.cursor.fetchall()
            filas.extend(materias)

        # Limpia la tabla antes de llenarla para evitar filas en blanco
        self.table.setRowCount(0)
        self.table.clearContents()
        self.table.setRowCount(len(filas))
        for i, (codigo, nombre, costo_unitario, cantidad) in enumerate(filas):
            if codigo is None:
                # Es un título de proceso/paso
                item = QTableWidgetItem(nombre)
                item.setFlags(Qt.ItemIsEnabled)
                item.setTextAlignment(Qt.AlignCenter)
                font = item.font()
                font.setBold(True)
                item.setFont(font)
                item.setBackground(Qt.lightGray)
                self.table.setItem(i, 0, item)
                self.table.setSpan(i, 0, 1, 4)
            else:
                self.table.setItem(i, 0, QTableWidgetItem(str(codigo)))
                self.table.setItem(i, 1, QTableWidgetItem(str(nombre)))
                self.table.setItem(i, 2, QTableWidgetItem(str(costo_unitario)))
                self.table.setItem(i, 3, QTableWidgetItem(str(cantidad)))