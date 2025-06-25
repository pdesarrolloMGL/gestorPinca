from models.detalle_factura import DetalleFacturaModel

class DetalleFacturaController:
    def __init__(self):
        self.model = DetalleFacturaModel()

    def agregar_detalle(self, factura_id, item_id, cantidad, precio_unitario):
        # Agregar detalle y descontar inventario
        detalle_id = self.model.agregar_detalle(factura_id, item_id, cantidad, precio_unitario)
        self.model.descontar_inventario(item_id, cantidad)
        return detalle_id

    def obtener_detalle_factura(self, factura_id):
        return self.model.obtener_detalle_factura(factura_id)

    def adicionar_inventario(self, item_id, cantidad, descripcion="ADICION MANUAL", referencia_id=None, referencia_tipo="COMPRA"):
        return self.model.adicionar_inventario(item_id, cantidad, descripcion, referencia_id, referencia_tipo)