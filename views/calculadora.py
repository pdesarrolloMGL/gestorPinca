from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox, QTableWidget, QTableWidgetItem, QHBoxLayout, QPushButton, QDialog
)
from PyQt5.QtCore import Qt
from .formulario_producto import FormularioProducto
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

        # Layout horizontal para select, input y botón
        selector_layout = QHBoxLayout()
        selector_layout.setAlignment(Qt.AlignCenter)

        # ComboBox para seleccionar producto
        self.producto_combo = QComboBox()
        self.producto_combo.addItem("Seleccione un producto...", None)  # Opción vacía por defecto
        self.productos = self.obtener_productos()
        for prod_id, nombre in self.productos:
            self.producto_combo.addItem(nombre, prod_id)
        self.producto_combo.currentIndexChanged.connect(self.mostrar_formula_producto)
        selector_layout.addWidget(self.producto_combo)

        self.btn_formulario = QPushButton("Calcular por producto")
        self.btn_formulario.setObjectName("btnFormulario")
        self.btn_formulario.clicked.connect(self.abrir_formulario_producto)
        selector_layout.addWidget(self.btn_formulario)

        main_layout.addLayout(selector_layout)

        # Tabla para mostrar materia prima usada por proceso
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["CODIGO", "MATERIA PRIMA", "COSTO UNITARIO", "CANTIDAD USADA", "TOTAL"])
        main_layout.addWidget(self.table)

        # Label para mostrar la suma total
        self.total_label = QLabel("TOTAL: $ 0.00")
        self.total_label.setObjectName("SumaTotalLabel")
        self.total_label.setAlignment(Qt.AlignRight)
        main_layout.addWidget(self.total_label)

        # No mostrar fórmula al iniciar
        # self.mostrar_formula_producto()

    def abrir_formulario_producto(self):
        dialog = FormularioProducto(self.productos, self)
        if dialog.exec_() == QDialog.Accepted:
            prod_id = dialog.producto_combo.currentData()
            volumen = dialog.volumen_input.text()
            # Aquí puedes hacer lo que quieras con prod_id y volumen
            print(f"Producto: {prod_id}, Volumen: {volumen}")

    def obtener_productos(self):
        self.cursor.execute("SELECT id, nombre FROM productos")
        return self.cursor.fetchall()

    def mostrar_formula_producto(self):
        prod_id = self.producto_combo.currentData()
        if prod_id is None:
            self.table.setRowCount(0)
            self.table.clearContents()
            self.total_label.setText("TOTAL: $ 0.00")
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
            filas.append((None, f"--- {descripcion} ---", None, None, None))
            # Materias primas de este paso
            self.cursor.execute("""
                SELECT mp.codigo, mp.nombre, mp.costo_unitario, pmp.cantidad
                FROM paso_materia_prima pmp
                JOIN materia_prima mp ON pmp.materia_prima_id = mp.id
                WHERE pmp.paso_id = ?
            """, (paso_id,))
            materias = self.cursor.fetchall()
            # Calcula el total para cada materia prima
            for codigo, nombre, costo_unitario, cantidad in materias:
                try:
                    total = float(costo_unitario) * float(cantidad)
                except Exception:
                    total = 0.0
                filas.append((codigo, nombre, costo_unitario, cantidad, total))

        # Limpia la tabla antes de llenarla para evitar filas en blanco
        self.table.setRowCount(0)
        self.table.clearContents()
        self.table.setColumnCount(5 + 1)
        self.table.setHorizontalHeaderLabels(["N°", "CODIGO", "MATERIA PRIMA", "COSTO UNITARIO", "CANTIDAD USADA", "TOTAL"])
        self.table.verticalHeader().setVisible(False)
        self.table.setRowCount(len(filas))
        suma_total = 0.0
        contador = 1
        for i, (codigo, nombre, costo_unitario, cantidad, total) in enumerate(filas):
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
                self.table.setSpan(i, 0, 1, 6)
            else:
                self.table.setItem(i, 0, QTableWidgetItem(str(contador)))
                self.table.setItem(i, 1, QTableWidgetItem(str(codigo)))
                self.table.setItem(i, 2, QTableWidgetItem(str(nombre)))
                # Formato moneda para costo unitario
                try:
                    costo_unitario_fmt = "$ {:,.2f}".format(float(costo_unitario))
                except Exception:
                    costo_unitario_fmt = str(costo_unitario)
                self.table.setItem(i, 3, QTableWidgetItem(costo_unitario_fmt))
                self.table.setItem(i, 4, QTableWidgetItem(str(cantidad)))
                # Formato moneda para total
                try:
                    total_fmt = "$ {:,.2f}".format(float(total))
                except Exception:
                    total_fmt = str(total)
                self.table.setItem(i, 5, QTableWidgetItem(total_fmt))
                # Sumar solo los totales de materias primas (no títulos)
                try:
                    suma_total += float(total)
                except Exception:
                    pass
                contador += 1

        self.total_label.setText(f"TOTAL: $ {suma_total:,.2f}")