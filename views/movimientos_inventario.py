# views/movimientos_inventario.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QLineEdit, QLabel, QComboBox, QGroupBox, QHeaderView, QMessageBox, QDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from controllers.movimientos_inventario_controller import MovimientosInventarioController
from controllers.inventario_controller import InventarioController

class MovimientosInventario(QWidget):
    def __init__(self):
        super().__init__()
        self.controller = MovimientosInventarioController()
        self.inventario_controller = InventarioController()
        
        layout = QVBoxLayout(self)

        # Título
        titulo = QLabel("Movimientos de Inventario")
        titulo.setObjectName("Titulo")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("""
            QLabel#Titulo {
                font-size: 22px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 18px;
            }
        """)
        layout.addWidget(titulo)

        # Filtros
        filtros_group = QGroupBox("Filtros")
        filtros_layout = QHBoxLayout()

        self.filtro_input = QLineEdit()
        self.filtro_input.setPlaceholderText("Buscar producto o descripción...")
        self.filtro_input.textChanged.connect(self.cargar_movimientos)

        self.combo_producto = QComboBox()
        self.combo_producto.addItem("Todos los productos", None)
        self.cargar_productos()
        self.combo_producto.currentTextChanged.connect(self.cargar_movimientos)

        self.combo_tipo = QComboBox()
        self.combo_tipo.addItems(["Todos", "entrada", "salida", "ajuste", "produccion"])
        self.combo_tipo.currentTextChanged.connect(self.cargar_movimientos)

        filtros_layout.addWidget(QLabel("Buscar:"))
        filtros_layout.addWidget(self.filtro_input)
        filtros_layout.addWidget(QLabel("Producto:"))
        filtros_layout.addWidget(self.combo_producto)
        filtros_layout.addWidget(QLabel("Tipo:"))
        filtros_layout.addWidget(self.combo_tipo)

        filtros_group.setLayout(filtros_layout)
        layout.addWidget(filtros_group)

        # Estadísticas
        self.stats_label = QLabel()
        self.stats_label.setStyleSheet("font-weight: bold; background-color: #ecf0f1; padding: 10px; border-radius: 5px;")
        layout.addWidget(self.stats_label)

        # Tabla de movimientos
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(8)
        self.tabla.setHorizontalHeaderLabels([
            "ID", "Producto", "Tipo", "Cantidad", "Fecha", "Descripción", "Ref. ID", "Ref. Tipo"
        ])
        self.tabla.horizontalHeader().setStretchLastSection(True)
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setStyleSheet("""
            QTableWidget {
                background: #ffffff;
                border: 1px solid #bfc9d1;
                border-radius: 8px;
                font-size: 15px;
                selection-background-color: #0083CB;
                gridline-color: #bfc9d1;
            }
        """)
        layout.addWidget(self.tabla)

        # Botones
        btn_layout = QHBoxLayout()
        self.btn_registrar_ajuste = QPushButton("Registrar Ajuste Manual")
        self.btn_registrar_ajuste.setObjectName("btnVerde")
        self.btn_registrar_ajuste.clicked.connect(self.registrar_ajuste_manual)
        btn_layout.addWidget(self.btn_registrar_ajuste)

        self.btn_exportar = QPushButton("Exportar CSV")
        self.btn_exportar.clicked.connect(self.exportar_csv)
        btn_layout.addWidget(self.btn_exportar)

        layout.addLayout(btn_layout)

        # Cargar datos iniciales
        self.cargar_movimientos()
        self.cargar_estadisticas()

    def cargar_productos(self):
        try:
            productos = self.inventario_controller.get_productos()
            for producto in productos:
                self.combo_producto.addItem(producto[1], producto[0])  # nombre, codigo
        except Exception as e:
            print(f"Error cargando productos: {e}")

    def cargar_movimientos(self):
        filtro = self.filtro_input.text() if self.filtro_input.text() else None
        item_codigo = self.combo_producto.currentData()
        
        # Obtener item_id por código si está seleccionado
        item_id = None
        if item_codigo:
            try:
                # Buscar el item_id en item_general por código
                from data.connection import get_connection
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM item_general WHERE codigo = ?", (item_codigo,))
                result = cursor.fetchone()
                item_id = result[0] if result else None
            except Exception as e:
                print(f"Error obteniendo item_id: {e}")
        
        movimientos = self.controller.get_movimientos(filtro, item_id)
        
        # Filtrar por tipo si no es "Todos"
        tipo_seleccionado = self.combo_tipo.currentText()
        if tipo_seleccionado != "Todos":
            movimientos = [m for m in movimientos if m[2] == tipo_seleccionado]

        self.tabla.setRowCount(0)
        for movimiento in movimientos:
            row = self.tabla.rowCount()
            self.tabla.insertRow(row)
            
            for col, value in enumerate(movimiento):
                item = QTableWidgetItem(str(value) if value is not None else "")
                item.setTextAlignment(Qt.AlignCenter)
                
                # Colorear según tipo de movimiento
                if col == 2:  # Columna tipo_movimiento
                    if value == "entrada":
                        item.setBackground(QColor(144, 238, 144))  # Verde claro
                    elif value == "salida":
                        item.setBackground(QColor(255, 182, 193))  # Rosa claro
                    elif value == "ajuste":
                        item.setBackground(QColor(255, 255, 102))  # Amarillo
                
                # Formatear cantidad con decimales
                if col == 3:  # Columna cantidad
                    item.setText(f"{float(value):,.2f}")
                
                self.tabla.setItem(row, col, item)

    def cargar_estadisticas(self):
        try:
            stats = self.controller.get_estadisticas()
            if stats and stats[0] is not None:
                total_movimientos = stats[0] or 0
                total_entradas = stats[1] or 0
                total_salidas = stats[2] or 0
                
                self.stats_label.setText(
                    f"TOTAL MOVIMIENTOS: {total_movimientos} | "
                    f"TOTAL ENTRADAS: {total_entradas:,.2f} | "
                    f"TOTAL SALIDAS: {total_salidas:,.2f}"
                )
            else:
                self.stats_label.setText("📊 Sin movimientos registrados")
        except Exception as e:
            print(f"Error cargando estadísticas: {e}")
            self.stats_label.setText("📊 Error cargando estadísticas")

    def registrar_ajuste_manual(self):
        # Implementar diálogo para ajuste manual
        QMessageBox.information(self, "Función", "Función de ajuste manual pendiente de implementar")

    def exportar_csv(self):
        # Implementar exportación a CSV
        QMessageBox.information(self, "Función", "Función de exportar CSV pendiente de implementar")