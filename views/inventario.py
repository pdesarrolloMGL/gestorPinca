from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QStackedWidget, QLabel, QHBoxLayout,
    QDialog, QFormLayout, QSpinBox, QPushButton, QMessageBox, QLineEdit, QHeaderView, QComboBox
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

        self.table = QTableWidget()
        self.table.setObjectName("tablaInventario")
        self.table.setSizePolicy(self.table.sizePolicy().Expanding, self.table.sizePolicy().Expanding)
        self.table.verticalHeader().setVisible(False)
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
        dialog.resize(400, 250)
        form_layout = QFormLayout(dialog)
        codigo = QLineEdit()
        codigo.setObjectName("codigoMateriaPrima")
        nombre = QLineEdit()
        nombre.setObjectName("nombreMateriaPrima")
        cantidad = QSpinBox()
        cantidad.setObjectName("cantidadMateriaPrima")
        cantidad.setMaximum(1000000)
        tipo = QComboBox()
        tipo.setObjectName("tipoMateriaPrima")
        tipo.addItems(["MATERIA PRIMA", "INSUMO"])
        form_layout.addRow("Código:", codigo)
        form_layout.addRow("Nombre:", nombre)
        form_layout.addRow("Cantidad:", cantidad)
        form_layout.addRow("Tipo:", tipo)
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
                    tipo.currentText()
                )
                QMessageBox.information(self, "Éxito", "Materia prima agregada correctamente.")
                dialog.accept()
                self.buscador_widget.input.clear()
                self.mostrar_materia_prima()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

        btn_guardar.clicked.connect(guardar)
        dialog.exec_()

    def abrir_sumar_materia_prima(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Sumar cantidad a materia prima")
        dialog.resize(400, 200)
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
        resultados = self.controller.get_productos(filtro)
        columnas = ["N°", "CODIGO", "NOMBRE", "COSTO UNITARIO", "TIPO", "CANTIDAD", "ELIMINAR"]
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