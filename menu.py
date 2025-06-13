from PyQt5.QtWidgets import QMainWindow, QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QStackedWidget, QSizePolicy
from PyQt5.QtCore import Qt
# from views.clientes import Clientes
# from views.costos import Costos
# from views.facturacion import Facturacion
from views.inventario import Inventario
from views.formulaciones import Formulaciones
# from views.produccion import Produccion
from PyQt5.QtGui import QPixmap, QIcon

class Menu(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon("assets/icon.ico"))
        self.setWindowTitle("Pinca S.A.S")
        self.setGeometry(100, 100, 1000, 600)
        self.showMaximized()

        # Vista principal
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        central_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        main_layout = QHBoxLayout(central_widget)

        # ───── BARRA LATERAL ─────
        sidebar = QWidget()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(200)
        sidebar_layout = QVBoxLayout()
        sidebar.setLayout(sidebar_layout)

        # Widget de logo inicial
        logo_widget = QWidget()
        logo_layout = QVBoxLayout(logo_widget)
        logo_label = QLabel()
        logo_pixmap = QPixmap("assets/pincalogo.png")
        if not logo_pixmap.isNull():
            logo_pixmap = logo_pixmap.scaled(500, 500, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(logo_pixmap)
        else:
            logo_label.setText("Logo no encontrado")
        logo_label.setAlignment(Qt.AlignCenter)
        logo_layout.addWidget(logo_label)
        logo_layout.addStretch()

        # Diccionario para guardar los botones
        self.sidebar_buttons = {}

        # Instancia las vistas, que ahora deben consultar la nueva base de datos
        botones = {
            "Inventario": Inventario(),     # Asegúrate que Inventario use la nueva base y modelo
            "Formulaciones": Formulaciones(),
            # "Clientes": Clientes(),
            # "Costos": Costos(),
            # "Facturación": Facturacion(),
            # "Producción": Produccion()
        }

        self.stack = QStackedWidget()
        self.stack.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.stack.addWidget(logo_widget)  # Logo como primera página 

        for nombre, widget in botones.items():
            btn = QPushButton(nombre)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setObjectName(f"SidebarBtn_{nombre.lower()}")
            btn.setProperty("active", False)
            btn.clicked.connect(lambda _, w=widget, n=nombre: self.cambiar_vista(w, n))
            sidebar_layout.addWidget(btn)
            self.stack.addWidget(widget)
            self.sidebar_buttons[nombre] = btn
        
        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.stack)
        self.stack.setCurrentIndex(0)

        # Botón de salida
        btn_salir = QPushButton("Salir")
        btn_salir.setObjectName("BotonSalir")
        btn_salir.setCursor(Qt.PointingHandCursor)
        btn_salir.clicked.connect(self.close)
        sidebar_layout.addWidget(btn_salir)

        sidebar_layout.addStretch()

    def cambiar_vista(self, widget, nombre):
        self.stack.setCurrentWidget(widget)
        # Quita el estilo activo de todos
        for btn in self.sidebar_buttons.values():
            btn.setProperty("active", False)
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        # Activa solo el botón actual
        btn_actual = self.sidebar_buttons[nombre]
        btn_actual.setProperty("active", True)
        btn_actual.style().unpolish(btn_actual)
        btn_actual.style().polish(btn_actual)