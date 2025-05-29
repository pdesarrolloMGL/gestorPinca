from PyQt5.QtWidgets import QApplication
from menu import Menu
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)

    with open("resources/estilos.qss", "r") as f:
        app.setStyleSheet(f.read())

    ventana = Menu()
    ventana.show()
    sys.exit(app.exec_())
