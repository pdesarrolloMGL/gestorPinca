from models.facturas import FacturasModel

class FacturasController:
    def __init__(self):
        self.model = FacturasModel()

    def get_facturas(self, filtro=None):
        """Obtener todas las facturas"""
        try:
            return self.model.obtener_facturas(filtro)
        except Exception as e:
            print(f"Error obteniendo facturas: {e}")
            return []

    def create_factura(self, numero, cliente_id, fecha, total, estado, subtotal, impuestos, descuento):
        """Crear nueva factura"""
        try:
            return self.model.agregar_factura(
                numero, cliente_id, fecha, total, estado, subtotal, impuestos, descuento
            )
        except Exception as e:
            print(f"Error creando factura: {e}")
            return None

    def agregar_factura(self, numero, cliente_id, fecha_emision, total, estado, subtotal, impuestos, retencion):
        """Método compatible con tu vista existente"""
        try:
            return self.model.agregar_factura(
                numero, cliente_id, fecha_emision, total, estado, subtotal, impuestos, retencion
            )
        except Exception as e:
            print(f"Error agregando factura: {e}")
            return None

    # ✅ MÉTODO PARA NUMERACIÓN AUTOMÁTICA
    def generar_numero_automatico(self):
        """Generar número automático"""
        try:
            return self.model.generar_numero_automatico()
        except Exception as e:
            print(f"Error en controlador generando número: {e}")
            # Fallback simple
            from datetime import datetime
            timestamp = int(datetime.now().timestamp())
            return f"FAC-{timestamp}"

    def existe_numero_factura(self, numero):
        """Verificar si existe el número"""
        try:
            return self.model.existe_numero_factura(numero)
        except Exception as e:
            print(f"Error verificando número: {e}")
            return False

    def eliminar_factura(self, factura_id):
        """Eliminar factura"""
        try:
            return self.model.eliminar_factura(factura_id)
        except Exception as e:
            print(f"Error eliminando factura: {e}")
            return False