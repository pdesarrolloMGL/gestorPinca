from data.connection import get_connection

class FacturasModel:
    def __init__(self):
        self.conn = get_connection()
        self.cursor = self.conn.cursor()

    def obtener_facturas(self, filtro=None):
        query = """
            SELECT f.id, f.numero, f.cliente_id, c.nombre_encargado || ' / ' || IFNULL(c.nombre_empresa, '') AS cliente, 
                f.fecha_emision, f.total, f.estado, f.subtotal, f.impuestos
            FROM facturas f
            JOIN clientes c ON f.cliente_id = c.id
        """
        params = ()
        if filtro:
            query += " WHERE f.numero LIKE ? OR c.nombre_encargado LIKE ? OR c.nombre_empresa LIKE ?"
            params = (f"%{filtro}%", f"%{filtro}%", f"%{filtro}%")
        query += " ORDER BY f.fecha_emision DESC"
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def agregar_factura(self, numero, cliente_id, fecha_emision, total, estado, subtotal, impuestos, retencion):
        self.cursor.execute(
            "INSERT INTO facturas (numero, cliente_id, fecha_emision, total, estado, subtotal, impuestos, retencion) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (numero, cliente_id, fecha_emision, total, estado, subtotal, impuestos, retencion)
        )
        self.conn.commit()
        return self.cursor.lastrowid

    def eliminar_factura(self, factura_id):
        self.cursor.execute("DELETE FROM facturas WHERE id = ?", (factura_id,))
        self.conn.commit()
    