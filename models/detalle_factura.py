# models/detalle_factura.py
from data.connection import get_connection

class DetalleFacturaModel:
    def __init__(self):
        self.conn = get_connection()
        self.cursor = self.conn.cursor()

    def agregar_detalle(self, factura_id, item_id, cantidad, precio_unitario):
        subtotal = cantidad * precio_unitario
        self.cursor.execute(
            "INSERT INTO detalle_facturas (factura_id, item_id, cantidad, precio_unitario, subtotal) VALUES (?, ?, ?, ?, ?)",
            (factura_id, item_id, cantidad, precio_unitario, subtotal)
        )
        
        # Descontar del inventario
        self.cursor.execute(
            "UPDATE inventario SET cantidad = cantidad - ? WHERE item_id = ?",
            (cantidad, item_id)
        )
        
        # Registrar movimiento de inventario
        from controllers.movimientos_inventario_controller import MovimientosInventarioController
        movimientos_controller = MovimientosInventarioController()
        movimientos_controller.registrar_salida_venta(item_id, cantidad, factura_id)
        
        self.conn.commit()
        return self.cursor.lastrowid

    def obtener_detalle_factura(self, factura_id):
        # CORREGIR: cambiar 'productos p' por 'item_general ig'
        self.cursor.execute(
            """SELECT df.id, ig.nombre, df.cantidad, df.precio_unitario, df.subtotal 
               FROM detalle_facturas df
               JOIN item_general ig ON df.item_id = ig.id
               WHERE df.factura_id = ?""",
            (factura_id,)
        )
        return self.cursor.fetchall()

    def descontar_inventario(self, item_id, cantidad):
        # CORREGIR: cambiar 'productos' por 'inventario'
        self.cursor.execute(
            "UPDATE inventario SET cantidad = cantidad - ? WHERE item_id = ?",
            (cantidad, item_id)
        )
        self.conn.commit()

    def adicionar_inventario(self, item_id, cantidad, descripcion="Adición manual", referencia_id=None, referencia_tipo="compra"):
        # Actualizar cantidad en inventario
        self.cursor.execute(
            "UPDATE inventario SET cantidad = cantidad + ? WHERE item_id = ?",
            (cantidad, item_id)
        )
        
        # Registrar movimiento de inventario
        from controllers.movimientos_inventario_controller import MovimientosInventarioController
        movimientos_controller = MovimientosInventarioController()
        movimientos_controller.registrar_movimiento(
            item_id, 
            'entrada', 
            cantidad, 
            descripcion, 
            referencia_id, 
            referencia_tipo
        )
        
        self.conn.commit()
        return True