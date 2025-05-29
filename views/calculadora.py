from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout

class Calculadora(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Pantalla de Calculadora"))
        self.setLayout(layout)