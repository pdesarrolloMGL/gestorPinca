from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QStackedWidget, QLabel, QHBoxLayout,
    QDialog, QFormLayout, QSpinBox, QPushButton, QMessageBox, QLineEdit
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from controllers.inventario_controller import InventarioController
from components.buscador import Buscador
from components.botonera_tabla import BotoneraTablas
from utils.table_utils import limpiar_celdas_widget, formatear_moneda

class Inventario(QWidget):
    def __init__(self):
        super().__init__()
        self.controller = InventarioController()
        self.stacked = QStackedWidget(self)
        self.pantalla_inventario = QWidget()
        main_layout = QVBoxLayout(self.pantalla_inventario)
        main_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        self.titulo_label = QLabel("Inventario de Productos")
        self.titulo_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.titulo_label)

        self.buscador_widget = Buscador("Buscar por nombre, código o tipo...", self.buscar)
        main_layout.addWidget(self.buscador_widget)

        self.botonera = BotoneraTablas(self.mostrar_productos, self.mostrar_materia_prima, self.abrir_agregar)
        main_layout.addWidget(self.botonera)

        self.table = QTableWidget()
        self.table.setSizePolicy(self.table.sizePolicy().Expanding, self.table.sizePolicy().Expanding)
        self.table.verticalHeader().setVisible(False)
        self.table.setMinimumHeight(300)
        self.table.setMinimumWidth(600)
        self.table.horizontalHeader().setSectionResizeMode(self.table.horizontalHeader().Stretch)
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
        if self.tabla_actual == "productos":
            self.abrir_formulario_producto()
        else:
            self.abrir_formulario_materia_prima()

    def abrir_formulario_producto(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Nuevo Producto")
        form_layout = QFormLayout(dialog)
        codigo = QLineEdit()
        nombre = QLineEdit()
        cantidad = QSpinBox()
        cantidad.setMaximum(1000000)
        form_layout.addRow("Código:", codigo)
        form_layout.addRow("Nombre:", nombre)
        form_layout.addRow("Cantidad:", cantidad)
        btn_guardar = QPushButton("Guardar")
        form_layout.addRow(btn_guardar)
        dialog.setLayout(form_layout)

        def guardar():
            try:
                # Solo agrega a item_general, inventario
                self.controller.model.cursor.execute(
                    "INSERT INTO item_general (codigo, nombre, tipo) VALUES (?, ?, 'producto')",
                    (codigo.text(), nombre.text())
                )
                self.controller.model.conn.commit()
                item_id = self.controller.model.cursor.lastrowid
                self.controller.model.cursor.execute(
                    "INSERT INTO inventario (item_id, cantidad, fecha_actualiz) VALUES (?, ?, datetime('now'))",
                    (item_id, cantidad.value())
                )
                self.controller.model.conn.commit()
                QMessageBox.information(self, "Éxito", "Producto agregado correctamente.")
                dialog.accept()
                self.mostrar_productos()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

        btn_guardar.clicked.connect(guardar)
        dialog.exec_()

    def abrir_formulario_materia_prima(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Nueva Materia Prima")
        form_layout = QFormLayout(dialog)
        codigo = QLineEdit()
        nombre = QLineEdit()
        cantidad = QSpinBox()
        cantidad.setMaximum(1000000)
        form_layout.addRow("Código:", codigo)
        form_layout.addRow("Nombre:", nombre)
        form_layout.addRow("Cantidad:", cantidad)
        btn_guardar = QPushButton("Guardar")
        form_layout.addRow(btn_guardar)
        dialog.setLayout(form_layout)

        def guardar():
            try:
                self.controller.add_materia_prima(codigo.text(), nombre.text(), cantidad.value())
                QMessageBox.information(self, "Éxito", "Materia prima agregada correctamente.")
                dialog.accept()
                self.mostrar_materia_prima()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

        btn_guardar.clicked.connect(guardar)
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
            tipo = "producto" if tabla == "productos" else "materia_prima"
            self.controller.delete_item(codigo, tipo)
            if tabla == "productos":
                self.mostrar_productos()
            else:
                self.mostrar_materia_prima()

    def mostrar_productos(self, filtro=None):
        self.tabla_actual = "productos"
        self.titulo_label.setText("Inventario de Productos")
        self.botonera.btn_agregar.setText("Agregar producto")
        resultados = self.controller.get_productos(filtro)
        columnas = ["N°", "CODIGO", "NOMBRE", "COSTO UNITARIO", "TIPO", "CANTIDAD", "ELIMINAR"]
        limpiar_celdas_widget(self.table)
        self.table.setRowCount(len(resultados))
        self.table.setColumnCount(len(columnas))
        self.table.setHorizontalHeaderLabels(columnas)
        for i, fila in enumerate(resultados):
            self.table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
            for j, valor in enumerate(fila):
                item = QTableWidgetItem(str(valor))
                if columnas[j + 1] != "NOMBRE":
                    item.setTextAlignment(Qt.AlignCenter)
                if columnas[j + 1] == "COSTO UNITARIO":
                    item.setText(formatear_moneda(valor))
                self.table.setItem(i, j + 1, item)
            btn = QPushButton()
            btn.setIcon(QIcon("assets/trash.png"))
            btn.setToolTip("Eliminar fila")
            btn.clicked.connect(lambda _, row=i: self.eliminar_fila_por_boton(row, "productos"))
            self.table.setCellWidget(i, len(columnas) - 1, btn)

    def mostrar_materia_prima(self, filtro=None):
        self.tabla_actual = "materia_prima"
        self.titulo_label.setText("Inventario de Materia Prima")
        self.botonera.btn_agregar.setText("Agregar materia prima")
        resultados = self.controller.get_materias_primas(filtro)
        columnas = ["N°", "CODIGO", "NOMBRE", "COSTO UNITARIO", "CANTIDAD", "ELIMINAR"]
        limpiar_celdas_widget(self.table)
        self.table.setRowCount(len(resultados))
        self.table.setColumnCount(len(columnas))
        self.table.setHorizontalHeaderLabels(columnas)
        for i, fila in enumerate(resultados):
            self.table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
            for j, valor in enumerate(fila):
                item = QTableWidgetItem(str(valor))
                if columnas[j + 1] != "NOMBRE":
                    item.setTextAlignment(Qt.AlignCenter)
                if columnas[j + 1] == "COSTO UNITARIO":
                    item.setText(formatear_moneda(valor))
                self.table.setItem(i, j + 1, item)
            btn = QPushButton()
            btn.setIcon(QIcon("assets/trash.png"))
            btn.setToolTip("Eliminar fila")
            btn.clicked.connect(lambda _, row=i: self.eliminar_fila_por_boton(row, "materia_prima"))
            self.table.setCellWidget(i, len(columnas) - 1, btn)