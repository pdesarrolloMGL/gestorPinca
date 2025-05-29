from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout

class Produccion(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Pantalla de Produccion"))
        self.setLayout(layout)