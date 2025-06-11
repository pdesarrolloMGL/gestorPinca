from data.connection import get_connection

class InventarioModel:
    def __init__(self):
        self.conn = get_connection()
        self.cursor = self.conn.cursor()
        
    def obtener_productos(self, filtro=None):
        query = """
            SELECT ig.codigo, ig.nombre, IFNULL(cp.costo_unitario, 0), ig.tipo, IFNULL(inv.cantidad, 0)
            FROM item_general ig
            LEFT JOIN inventario inv ON ig.id = inv.item_id
            LEFT JOIN costos_produccion cp ON ig.id = cp.item_id
            WHERE UPPER(ig.tipo) = 'PRODUCTO'
        """
        params = ()
        if filtro:
            query += " AND (lower(ig.codigo) LIKE ? OR lower(ig.nombre) LIKE ? OR lower(ig.tipo) LIKE ?)"
            params = (f"%{filtro}%", f"%{filtro}%", f"%{filtro}%")
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def obtener_materias_primas(self, filtro=None):
        query = """
            SELECT ig.codigo, ig.nombre, IFNULL(cp.costo_unitario, 0), IFNULL(inv.cantidad, 0)
            FROM item_general ig
            LEFT JOIN inventario inv ON ig.id = inv.item_id
            LEFT JOIN costos_produccion cp ON ig.id = cp.item_id
            WHERE UPPER(ig.tipo) = 'MATERIA PRIMA'
        """
        params = ()
        if filtro:
            query += " AND (lower(ig.codigo) LIKE ? OR lower(ig.nombre) LIKE ?)"
            params = (f"%{filtro}%", f"%{filtro}%")
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def agregar_materia_prima(self, codigo, nombre, cantidad):
        self.cursor.execute(
            "INSERT INTO item_general (codigo, nombre, tipo) VALUES (?, ?, 'materia_prima')",
            (codigo, nombre)
        )
        self.conn.commit()
        item_id = self.cursor.lastrowid
        self.cursor.execute(
            "INSERT INTO inventario (item_id, cantidad, fecha_actualiz) VALUES (?, ?, datetime('now'))",
            (item_id, cantidad)
        )
        self.conn.commit()

    def eliminar_item(self, codigo, tipo):
        self.cursor.execute(
            "DELETE FROM item_general WHERE codigo = ? AND tipo = ?",
            (codigo, tipo)
        )
        self.conn.commit()