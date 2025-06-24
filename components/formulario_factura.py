from PyQt5.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QComboBox, QDateEdit, QDoubleSpinBox, QDialogButtonBox
)
from PyQt5.QtCore import QDate

class FormularioFactura(QDialog):
    def __init__(self, clientes, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Crear Factura")
        layout = QFormLayout(self)

        self.input_numero = QLineEdit()
        self.combo_cliente = QComboBox()
        self.combo_cliente.addItem("Sin cliente", None)
        for cliente in clientes:
            # cliente: (id, nombre_encargado, nombre_empresa)
            nombre = f"{cliente[1]} / {cliente[2]}" if cliente[2] else cliente[1]
            self.combo_cliente.addItem(nombre, cliente[0])

        self.input_fecha = QDateEdit(QDate.currentDate())
        self.input_fecha.setCalendarPopup(True)
        self.input_total = QDoubleSpinBox()
        self.input_total.setMaximum(1e9)
        self.input_total.setPrefix("$")
        self.input_total.setDecimals(2)
        self.input_subtotal = QDoubleSpinBox()
        self.input_subtotal.setMaximum(1e9)
        self.input_subtotal.setPrefix("$")
        self.input_subtotal.setDecimals(2)
        self.input_impuestos = QDoubleSpinBox()
        self.input_impuestos.setMaximum(1e9)
        self.input_impuestos.setPrefix("$")
        self.input_impuestos.setDecimals(2)
        self.input_retencion = QDoubleSpinBox()
        self.input_retencion.setMaximum(1e9)
        self.input_retencion.setPrefix("$")
        self.input_retencion.setDecimals(2)
        self.input_estado = QLineEdit("PENDIENTE")

        layout.addRow("N° Factura:", self.input_numero)
        layout.addRow("Cliente:", self.combo_cliente)
        layout.addRow("Fecha:", self.input_fecha)
        layout.addRow("Total:", self.input_total)
        layout.addRow("Subtotal:", self.input_subtotal)
        layout.addRow("Impuestos:", self.input_impuestos)
        layout.addRow("Retención:", self.input_retencion)
        layout.addRow("Estado:", self.input_estado)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    def get_data(self):
        return (
            self.input_numero.text(),
            self.combo_cliente.currentData(),
            self.input_fecha.date().toString("yyyy-MM-dd"),
            float(self.input_total.value()),
            self.input_estado.text(),
            float(self.input_subtotal.value()),
            float(self.input_impuestos.value()),
            float(self.input_retencion.value())
        )