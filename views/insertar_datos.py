from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QMessageBox
)
from PyQt5.QtCore import Qt
from data.connection import get_connection

class InsertarDatos(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Insertar Costo")

        layout = QVBoxLayout()

        titulo = QLabel("Insertar nuevo costo")
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)

        # Campos de entrada
        self.descripcion_input = QLineEdit()
        self.descripcion_input.setPlaceholderText("Descripción")
        layout.addWidget(self.descripcion_input)

        self.monto_input = QLineEdit()
        self.monto_input.setPlaceholderText("Monto")
        layout.addWidget(self.monto_input)

        self.fecha_input = QLineEdit()
        self.fecha_input.setPlaceholderText("Fecha (YYYY-MM-DD)")
        layout.addWidget(self.fecha_input)

        # Botón de insertar
        btn_insertar = QPushButton("Insertar")
        btn_insertar.clicked.connect(self.insertar_costo)
        layout.addWidget(btn_insertar)

        self.setLayout(layout)

    def insertar_costo(self):
        descripcion = self.descripcion_input.text()
        monto_text = self.monto_input.text()
        fecha = self.fecha_input.text()

        # Validación básica
        if not descripcion or not monto_text or not fecha:
            QMessageBox.warning(self, "Campos incompletos", "Por favor, completa todos los campos.")
            return

        try:
            monto = float(monto_text)
        except ValueError:
            QMessageBox.warning(self, "Monto inválido", "El monto debe ser un número.")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO costos (descripcion, monto, fecha) VALUES (?, ?, ?)",
                (descripcion, monto, fecha)
            )
            conn.commit()
            conn.close()
            QMessageBox.information(self, "Éxito", "Costo insertado correctamente.")
            # Limpiar campos
            self.descripcion_input.clear()
            self.monto_input.clear()
            self.fecha_input.clear()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Ocurrió un error al insertar: {e}")