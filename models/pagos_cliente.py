from data.connection import get_connection

class PagosClienteModel:
    def __init__(self):
        self.conn = get_connection()
        self.cursor = self.conn.cursor()

    def registrar_pago(self, cliente_id, factura_id, monto, metodo_pago, observaciones):
        self.cursor.execute(
            "INSERT INTO pagos_cliente (cliente_id, factura_id, monto, metodo_pago, observaciones) VALUES (?, ?, ?, ?, ?)",
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