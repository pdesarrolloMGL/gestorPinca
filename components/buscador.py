from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton

class Buscador(QWidget):
    def __init__(self, placeholder, on_search):
        super().__init__()
        layout = QHBoxLayout(self)
        self.input = QLineEdit()
        self.input.setPlaceholderText(placeholder)
        btn = QPushButton("Buscar")
        btn.clicked.connect(lambda: on_search(self.input.text()))
        self.input.returnPressed.connect(lambda: on_search(self.input.text()))
        layout.addWidget(self.input)
        layout.addWidget(btn)