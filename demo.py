from PyQt5.QtWidgets import QApplication, QWidget, QLineEdit, QListWidget, QListWidgetItem, QVBoxLayout
from PyQt5.QtCore import Qt
import sys

class Demo(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Buscador flotante demo")
        self.setGeometry(100, 100, 400, 100)
        layout = QVBoxLayout(self)

        self.productos = [
            (1, "Producto Alfa"),
            (2, "Producto Beta"),
            (3, "Producto Gamma"),
            (4, "Producto Delta"),
        ]

        self.busqueda = QLineEdit()
        self.busqueda.setPlaceholderText("Buscar producto...")
        layout.addWidget(self.busqueda)

        self.dropdown = QListWidget()
        self.dropdown.setWindowFlags(Qt.Popup)
        self.dropdown.hide()

        self.busqueda.textChanged.connect(self.buscar)
        self.dropdown.itemClicked.connect(self.seleccionar)

    def buscar(self, texto):
        self.dropdown.clear()
        if not texto:
            self.dropdown.hide()
            return
        for prod_id, nombre in self.productos:
            if texto.lower() in nombre.lower():
                item = QListWidgetItem(nombre)
                item.setData(Qt.UserRole, prod_id)
                self.dropdown.addItem(item)
        if self.dropdown.count() > 0:
            pos = self.busqueda.mapToGlobal(self.busqueda.rect().bottomLeft())
            self.dropdown.move(pos)
            self.dropdown.setFixedWidth(self.busqueda.width())
            self.dropdown.setMinimumHeight(80)
            self.dropdown.setMaximumHeight(200)
            self.dropdown.raise_()
            self.dropdown.show()
        else:
            self.dropdown.hide()

    def seleccionar(self, item):
        self.busqueda.setText(item.text())
        self.dropdown.hide()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = Demo()
    demo.show()
    sys.exit(app.exec_())