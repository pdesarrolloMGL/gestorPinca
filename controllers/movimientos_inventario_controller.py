from models.movimientos_inventario import MovimientosInventarioModel

class MovimientosInventarioController:
    def __init__(self):
        self.model = MovimientosInventarioModel()

    def registrar_movimiento(self, item_id, tipo_movimiento, cantidad, descripcion, referencia_id=None, referencia_tipo=None):
        return self.model.registrar_movimiento(item_id, tipo_movimiento, cantidad, descripcion, referencia_id, referencia_tipo)

    def get_movimientos(self, filtro=None, item_id=None):
        return self.model.obtener_movimientos(filtro, item_id)

    def get_estadisticas(self):
        return self.model.obtener_estadisticas()

    # Métodos específicos para cada tipo de movimiento
    def registrar_entrada_compra(self, item_id, cantidad, proveedor, numero_factura):
        descripcion = f"Compra a {proveedor} - Factura: {numero_factura}"
        return self.registrar_movimiento(item_id, 'entrada', cantidad, descripcion, numero_factura, 'compra')

    def registrar_salida_venta(self, item_id, cantidad, factura_id):
        descripcion = f"Venta - Factura #{factura_id}"
        return self.registrar_movimiento(item_id, 'salida', cantidad, descripcion, factura_id, 'factura')

    def registrar_produccion(self, item_id, cantidad, orden_produccion_id):
        descripcion = f"Producción - Orden #{orden_produccion_id}"
        return self.registrar_movimiento(item_id, 'entrada', cantidad, descripcion, orden_produccion_id, 'produccion')

    def registrar_ajuste(self, item_id, cantidad, motivo):
        tipo = 'entrada' if cantidad > 0 else 'salida'
        descripcion = f"Ajuste manual: {motivo}"
        return self.registrar_movimiento(item_id, tipo, abs(cantidad), descripcion, None, 'ajuste_manual')