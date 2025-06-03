from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout, QLabel, QComboBox, QSpinBox, QMessageBox, QHeaderView, 
)
from PyQt5.QtCore import Qt
from data.connection import get_connection
from PyQt5.QtGui import QColor, QFont

class Produccion(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.conn = get_connection()
        self.cursor = self.conn.cursor()

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        # --- Widgets de producción ---
        self.titulo_label = QLabel("Producción")
        self.titulo_label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.titulo_label)

        self.agregar_layout = QHBoxLayout()
        self.agregar_layout.setAlignment(Qt.AlignCenter)

        self.lbl_producto = QLabel("Producto:")
        self.producto_combo = QComboBox()
        self.producto_combo.setMinimumWidth(200)
        self.producto_combo.addItem("Seleccione un producto...", None)
        self.cursor.execute("SELECT id, nombre FROM productos")
        for prod_id, nombre in self.cursor.fetchall():
            self.producto_combo.addItem(nombre, prod_id)
        self.agregar_layout.addWidget(self.lbl_producto)
        self.agregar_layout.addWidget(self.producto_combo)

        self.lbl_cantidad = QLabel("Cantidad:")
        self.cantidad_spin = QSpinBox()
        self.cantidad_spin.setMinimum(1)
        self.cantidad_spin.setMaximum(1000000)
        self.agregar_layout.addWidget(self.lbl_cantidad)
        self.agregar_layout.addWidget(self.cantidad_spin)

        self.btn_agregar = QPushButton("Agregar producción")
        self.btn_agregar.setObjectName("btnFormulario")
        self.btn_agregar.clicked.connect(self.agregar_produccion)
        self.agregar_layout.addWidget(self.btn_agregar)

        self.main_layout.addLayout(self.agregar_layout)

        self.lbl_mp = QLabel("Materia prima necesaria:")
        self.main_layout.addWidget(self.lbl_mp)
        self.table_mp = QTableWidget()
        self.table_mp.setColumnCount(4)
        self.table_mp.setHorizontalHeaderLabels([
            "MATERIA PRIMA", "CANTIDAD NECESARIA", "CANTIDAD DISPONIBLE", "COSTO UNITARIO"
        ])
        self.table_mp.verticalHeader().setVisible(False)
        self.table_mp.setSizePolicy(self.table_mp.sizePolicy().horizontalPolicy(), self.table_mp.sizePolicy().verticalPolicy())
        self.table_mp.horizontalHeader().setStretchLastSection(True)
        self.table_mp.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.main_layout.addWidget(self.table_mp)

        self.costo_total_label = QLabel("Costo total estimado: $ 0.00")
        self.costo_total_label.setObjectName("SumaTotalLabel")
        self.costo_total_label.setAlignment(Qt.AlignRight)
        self.main_layout.addWidget(self.costo_total_label)

        self.btn_ver_historial = QPushButton("Ver historial de producción")
        self.btn_ver_historial.clicked.connect(self.mostrar_historial)
        self.main_layout.addWidget(self.btn_ver_historial)

        # --- Widget de historial ---
        self.historial_widget = QWidget()
        self.historial_layout = QVBoxLayout(self.historial_widget)
        self.historial_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        self.table_historial = QTableWidget()
        self.table_historial.setColumnCount(5)
        self.table_historial.setHorizontalHeaderLabels([
            "N°", "Producto", "Cantidad", "Fecha", "Costo Total"
        ])
        self.table_historial.verticalHeader().setVisible(False)
        self.table_historial.setSizePolicy(self.table_historial.sizePolicy().horizontalPolicy(), self.table_historial.sizePolicy().verticalPolicy())
        self.table_historial.horizontalHeader().setStretchLastSection(True)
        self.table_historial.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.historial_layout.addWidget(self.table_historial)

        self.btn_volver = QPushButton("Volver")
        self.btn_volver.clicked.connect(self.volver_a_produccion)
        self.historial_layout.addWidget(self.btn_volver)

        self.historial_widget.setVisible(False)
        self.main_layout.addWidget(self.historial_widget)

        # Conectar cambios
        self.producto_combo.currentIndexChanged.connect(self.actualizar_materia_prima)
        self.cantidad_spin.valueChanged.connect(self.actualizar_materia_prima)

        self.cargar_historial()
        self.actualizar_materia_prima()

    def mostrar_historial(self):
        # Oculta todos los widgets de producción
        self.titulo_label.setVisible(False)
        self.lbl_producto.setVisible(False)
        self.producto_combo.setVisible(False)
        self.lbl_cantidad.setVisible(False)
        self.cantidad_spin.setVisible(False)
        self.btn_agregar.setVisible(False)
        self.lbl_mp.setVisible(False)
        self.table_mp.setVisible(False)
        self.costo_total_label.setVisible(False)
        self.btn_ver_historial.setVisible(False)
        # Muestra solo el historial
        self.historial_widget.setVisible(True)
        self.cargar_historial()

    def volver_a_produccion(self):
        # Muestra widgets de producción
        self.titulo_label.setVisible(True)
        self.lbl_producto.setVisible(True)
        self.producto_combo.setVisible(True)
        self.lbl_cantidad.setVisible(True)
        self.cantidad_spin.setVisible(True)
        self.btn_agregar.setVisible(True)
        self.lbl_mp.setVisible(True)
        self.table_mp.setVisible(True)
        self.costo_total_label.setVisible(True)
        self.btn_ver_historial.setVisible(True)
        # Oculta historial
        self.historial_widget.setVisible(False)

    def actualizar_materia_prima(self):
        prod_id = self.producto_combo.currentData()
        cantidad = self.cantidad_spin.value()
        if not prod_id:
            self.table_mp.setRowCount(0)
            self.costo_total_label.setText("Costo total estimado: $ 0.00")
            return
        self.cursor.execute("""
            SELECT mp.nombre, pmp.cantidad, mp.cantidad, mp.costo_unitario
            FROM producto_materia_prima pmp
            JOIN materia_prima mp ON pmp.materia_prima_id = mp.id
            WHERE pmp.producto_id = ?
        """, (prod_id,))
        materias = self.cursor.fetchall()
        self.table_mp.setRowCount(len(materias))
        costo_total = 0.0
        for i, (nombre, cantidad_necesaria, cantidad_disponible, costo_unitario) in enumerate(materias):
            total_necesaria = cantidad_necesaria * cantidad
            try:
                costo_unitario_fmt = "$ {:,.2f}".format(float(costo_unitario))
                costo_total += float(costo_unitario) * total_necesaria
            except Exception:
                costo_unitario_fmt = str(costo_unitario)
            # Nombre alineado a la izquierda (por defecto)
            self.table_mp.setItem(i, 0, QTableWidgetItem(str(nombre)))
            # Centrar cantidad necesaria
            item_necesaria = QTableWidgetItem(str(total_necesaria))
            item_necesaria.setTextAlignment(Qt.AlignCenter)
            self.table_mp.setItem(i, 1, item_necesaria)
            # Centrar cantidad disponible y colorear
            item_disponible = QTableWidgetItem(str(cantidad_disponible))
            item_disponible.setTextAlignment(Qt.AlignCenter)
            if cantidad_disponible >= total_necesaria:
                item_disponible.setBackground(QColor("#B6FCD5"))  # Verde pastel personalizado
            else:
                item_disponible.setBackground(QColor("#FFB6B6"))  # Rojo pastel personalizado
            self.table_mp.setItem(i, 2, item_disponible)
            # Centrar costo unitario
            item_costo = QTableWidgetItem(costo_unitario_fmt)
            item_costo.setTextAlignment(Qt.AlignCenter)
            self.table_mp.setItem(i, 3, item_costo)
        self.costo_total_label.setText(f"Costo total estimado: $ {costo_total:,.2f}")

    def cargar_historial(self):
        self.cursor.execute("""
            SELECT p.id, pr.nombre, p.cantidad, p.fecha, p.costo_total
            FROM produccion p
            JOIN productos pr ON p.producto_id = pr.id
            ORDER BY p.fecha DESC
        """)
        resultados = self.cursor.fetchall()
        self.table_historial.setRowCount(len(resultados))
        for i, fila in enumerate(resultados):
            for j, valor in enumerate(fila):
                if j == 4:
                    try:
                        valor = "$ {:,.2f}".format(float(valor))
                    except Exception:
                        pass
                self.table_historial.setItem(i, j, QTableWidgetItem(str(valor)))

    def agregar_produccion(self):
        prod_id = self.producto_combo.currentData()
        cantidad = self.cantidad_spin.value()
        if not prod_id:
            QMessageBox.warning(self, "Error", "Seleccione un producto.")
            return
        self.cursor.execute("""
            SELECT mp.nombre, pmp.cantidad, mp.cantidad, mp.costo_unitario
            FROM producto_materia_prima pmp
            JOIN materia_prima mp ON pmp.materia_prima_id = mp.id
            WHERE pmp.producto_id = ?
        """, (prod_id,))
        faltantes = []
        costo_total = 0.0
        materias = self.cursor.fetchall()
        for nombre, cantidad_necesaria, cantidad_disponible, costo_unitario in materias:
            total_necesaria = cantidad_necesaria * cantidad
            if cantidad_disponible < total_necesaria:
                faltantes.append(f"{nombre} (necesita {total_necesaria}, hay {cantidad_disponible})")
            try:
                costo_total += float(costo_unitario) * total_necesaria
            except Exception:
                pass
        if faltantes:
            QMessageBox.warning(self, "Materia prima insuficiente", "No hay suficiente materia prima:\n" + "\n".join(faltantes))
            return
        self.cursor.execute("""
            SELECT pmp.materia_prima_id, pmp.cantidad
            FROM producto_materia_prima pmp
            WHERE pmp.producto_id = ?
        """, (prod_id,))
        for mp_id, cantidad_necesaria in self.cursor.fetchall():
            total_necesaria = cantidad_necesaria * cantidad
            self.cursor.execute("UPDATE materia_prima SET cantidad = cantidad - ? WHERE id = ?", (total_necesaria, mp_id))
        self.cursor.execute(
            "INSERT INTO produccion (producto_id, cantidad, fecha, costo_total) VALUES (?, ?, DATE('now'), ?)",
            (prod_id, cantidad, costo_total)
        )
        self.conn.commit()
        QMessageBox.information(self, "Éxito", "Producción agregada correctamente.")
        self.cargar_historial()
        self.actualizar_materia_prima()