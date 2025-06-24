from models.facturas import FacturasModel

class FacturasController:
    def __init__(self):
        self.model = FacturasModel()

    def get_facturas(self, filtro=None):
        return self.model.obtener_facturas(filtro)

    def agregar_factura(self, numero, cliente_id, fecha_emision, total, estado, subtotal, impuestos, retencion):
        return self.model.agregar_factura(numero, cliente_id, fecha_emision, total, estado, subtotal, impuestos, retencion)

    def eliminar_factura(self, factura_id):
        self.model.eliminar_factura(factura_id)