from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QLineEdit, QPushButton
from PyQt5.QtCore import Qt

class FormularioProducto(QDialog):
    def __init__(self, productos, parent=None):
        super().__init__(parent)

        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
    
        # Título
        titulo = QLabel("Calcular Fórmula por Producto")
        titulo.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(titulo)

        # Select de producto
        self.producto_combo = QComboBox()
        self.producto_combo.addItem("Seleccione un producto...", None)
        for prod_id, nombre in productos:
            self.producto_combo.addItem(nombre, prod_id)
        main_layout.addWidget(QLabel("Producto:"))
        main_layout.addWidget(self.producto_combo)

        # Input de volumen
        self.volumen_input = QLineEdit()
        self.volumen_input.setPlaceholderText("Volumen")
        main_layout.addWidget(QLabel("Volumen:"))
        main_layout.addWidget(self.volumen_input)

        # Botón de aceptar
        self.btn_aceptar = QPushButton("Aceptar")
        self.btn_aceptar.clicked.connect(self.accept)
        main_layout.addWidget(self.btn_aceptar)