from data.connection import get_connection

class ClientesModel:
    def __init__(self):
        self.conn = get_connection()
        self.cursor = self.conn.cursor()

    def obtener_clientes(self, filtro=None):
        query = "SELECT id, nombre_encargado, nombre_empresa, numero_documento, direccion, telefono, email FROM clientes"
        params = ()
        if filtro:
            query += " WHERE nombre_encargado LIKE ? OR nombre_empresa LIKE ? OR numero_documento LIKE ?"
            params = (f"%{filtro}%", f"%{filtro}%", f"%{filtro}%")
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def agregar_cliente(self, nombre_encargado, nombre_empresa, numero_documento, direccion, telefono, email):
        self.cursor.execute(
            "INSERT INTO clientes (nombre_encargado, nombre_empresa, numero_documento, direccion, telefono, email) VALUES (?, ?, ?, ?, ?, ?)",
            (nombre_encargado, nombre_empresa, numero_documento, direccion, telefono, email)
        )
        self.conn.commit()
        return self.cursor.lastrowid

    def eliminar_cliente(self, cliente_id):
        self.cursor.execute("DELETE FROM clientes WHERE id = ?", (cliente_id,))
        self.conn.commit()
    
    def get_facturas_cliente(self, cliente_id):
        self.cursor.execute(
            "SELECT id, numero, fecha_emision, total, estado FROM facturas WHERE cliente_id = ? ORDER BY fecha_emision DESC",
            (cliente_id,)
        )
        return self.cursor.fetchall()

    def obtener_clientes_avanzado(self, filtro=None, empresa=None, saldo=None):
        query = "SELECT id, nombre_encargado, nombre_empresa, numero_documento, direccion, telefono, email FROM clientes WHERE 1=1"
        params = []
        if filtro:
            query += " AND (nombre_encargado LIKE ? OR nombre_empresa LIKE ? OR numero_documento LIKE ?)"
            params += [f"%{filtro}%", f"%{filtro}%", f"%{filtro}%"]
        if empresa:
            query += " AND nombre_empresa LIKE ?"
            params.append(f"%{empresa}%")
        if saldo:
            query += " AND id IN (SELECT cliente_id FROM facturas f LEFT JOIN pagos_cliente p ON f.id = p.factura_id GROUP BY cliente_id HAVING SUM(f.total) - IFNULL(SUM(p.monto),0) > ?)"
            params.append(float(saldo))
        self.cursor.execute(query, params)
        return self.cursor.fetchall()
    