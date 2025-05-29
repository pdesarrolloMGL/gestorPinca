from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout

class Facturacion(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Pantalla de Facturacion"))
        self.setLayout(layout)