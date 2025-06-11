from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton

class BotoneraTablas(QWidget):
    def __init__(self, on_productos, on_materia, on_agregar):
        super().__init__()
        layout = QHBoxLayout(self)
        self.btn_productos = QPushButton("Productos")
        self.btn_materia = QPushButton("Materia Prima")
        self.btn_agregar = QPushButton("Agregar producto")
        layout.addWidget(self.btn_productos)
        layout.addWidget(self.btn_materia)
        layout.addWidget(self.btn_agregar)
        self.btn_productos.clicked.connect(on_productos)
        self.btn_materia.clicked.connect(on_materia)
        self.btn_agregar.clicked.connect(on_agregar)