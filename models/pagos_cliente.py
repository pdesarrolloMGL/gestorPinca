from data.connection import get_connection

class PagosClienteModel:
    def __init__(self):
        self.conn = get_connection()
        self.cursor = self.conn.cursor()

    def registrar_pago(self, cliente_id, factura_id, monto, metodo_pago, observaciones):
        self.cursor.execute(
            "INSERT INTO pagos_cliente (cliente_id, factura_id, fecha_pago, monto, metodo_pago, observaciones) VALUES (?, ?, CURRENT_TIMESTAMP, ?, ?, ?)",
            (cliente_id, factura_id, monto, metodo_pago, observaciones)
        )
        self.conn.commit()
        return self.cursor.lastrowid

    def obtener_pagos_cliente(self, cliente_id):
        self.cursor.execute(
            "SELECT id, factura_id, fecha_pago, monto, metodo_pago, observaciones FROM pagos_cliente WHERE cliente_id = ? ORDER BY fecha_pago DESC",
            (cliente_id,)
        )
        return self.cursor.fetchall()

    def total_pagado(self, cliente_id):
        self.cursor.execute(
            "SELECT IFNULL(SUM(monto), 0) FROM pagos_cliente WHERE cliente_id = ?",
            (cliente_id,)
        )
        return float(self.cursor.fetchone()[0])

    def total_facturado(self, cliente_id):
        self.cursor.execute(
            "SELECT IFNULL(SUM(total), 0) FROM facturas WHERE cliente_id = ? AND estado != 'anulada'",
            (cliente_id,)
        )
        return float(self.cursor.fetchone()[0])

    def saldo_cliente(self, cliente_id):
        return round(self.total_facturado(cliente_id) - self.total_pagado(cliente_id), 2)
    
    def total_pagado_factura(self, factura_id):
        self.cursor.execute(
            "SELECT IFNULL(SUM(monto), 0) FROM pagos_cliente WHERE factura_id = ?",
            (factura_id,)
        )
        return float(self.cursor.fetchone()[0])

    def get_historial_pagos_cliente(self, cliente_id):
        self.cursor.execute("""
            SELECT p.id, p.fecha_pago, p.monto, p.metodo_pago
            FROM pagos_cliente p
            JOIN facturas f ON p.factura_id = f.id
            WHERE f.cliente_id = ?
            ORDER BY p.fecha_pago DESC
        """, (cliente_id,))
        return self.cursor.fetchall()

    def get_todos_los_pagos(self):
        """Obtiene todos los pagos con información del cliente"""
        self.cursor.execute("""
            SELECT p.id, p.cliente_id, p.factura_id, p.monto, p.metodo_pago, 
                   p.fecha_pago, p.observaciones, c.nombre_empresa || ' - ' || c.nombre_encargado as cliente_nombre
            FROM pagos_cliente p
            JOIN clientes c ON p.cliente_id = c.id
            ORDER BY p.fecha_pago DESC
        """)
        return self.cursor.fetchall()

    def get_pagos_por_factura(self, factura_id):
        """Obtener todos los pagos de una factura específica SIN el ID"""
        try:
            query = """
                SELECT fecha_pago, monto, metodo_pago, observaciones
                FROM pagos_cliente 
                WHERE factura_id = ?
                ORDER BY fecha_pago DESC
            """
            self.cursor.execute(query, (factura_id,))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error obteniendo pagos de factura {factura_id}: {e}")
            return []
    
    def get_pagos_por_factura_completo(self, factura_id):
        try:
            query = """
                SELECT 
                    p.id, 
                    p.cliente_id, 
                    p.factura_id, 
                    p.monto, 
                    p.metodo_pago, 
                    p.fecha_pago, 
                    p.observaciones,
                    c.nombre_encargado as nombre_cliente
                FROM pagos_cliente p
                JOIN clientes c ON p.cliente_id = c.id
                WHERE p.factura_id = ?
                ORDER BY p.fecha_pago DESC
            """
            self.cursor.execute(query, (factura_id,))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error obteniendo pagos completos de factura {factura_id}: {e}")
            return []