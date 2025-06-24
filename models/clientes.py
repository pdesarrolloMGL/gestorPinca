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