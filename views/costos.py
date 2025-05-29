from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout

class Costos(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Pantalla de Costos"))
        self.setLayout(layout)