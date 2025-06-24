from PyQt5.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QDialogButtonBox
)

class FormularioCliente(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Agregar Cliente")
        layout = QFormLayout(self)

        self.input_encargado = QLineEdit()
        self.input_empresa = QLineEdit()
        self.input_documento = QLineEdit()
        self.input_direccion = QLineEdit()
        self.input_telefono = QLineEdit()
        self.input_email = QLineEdit()

        layout.addRow("Encargado:", self.input_encargado)
        layout.addRow("Empresa:", self.input_empresa)
        layout.addRow("N° Documento:", self.input_documento)
        layout.addRow("Dirección:", self.input_direccion)
        layout.addRow("Teléfono:", self.input_telefono)
        layout.addRow("Email:", self.input_email)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    def get_data(self):
        return (
            self.input_encargado.text(),
            self.input_empresa.text(),
            self.input_documento.text(),
            self.input_direccion.text(),
            self.input_telefono.text(),
            self.input_email.text()
        )