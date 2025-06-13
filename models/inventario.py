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

    def agregar_materia_prima(self, codigo, nombre, cantidad, tipo):
        self.cursor.execute(
            "INSERT INTO item_general (codigo, nombre, tipo) VALUES (?, ?, ?)",
            (codigo, nombre, tipo)
        )
        self.conn.commit()
        item_id = self.cursor.lastrowid
        self.cursor.execute(
            "INSERT INTO inventario (item_id, cantidad, fecha_update) VALUES (?, ?, datetime('now'))",
            (item_id, cantidad)
        )
        self.conn.commit()

    def obtener_materias_primas(self, filtro=None):
        if filtro:
            self.cursor.execute("""
                SELECT ig.codigo, ig.nombre, ig.tipo, i.cantidad
                FROM item_general ig
                JOIN inventario i ON ig.id = i.item_id
                WHERE ig.tipo = 'MATERIA PRIMA'
                AND (ig.codigo LIKE ? OR ig.nombre LIKE ? OR ig.tipo LIKE ?)
            """, (f'%{filtro}%', f'%{filtro}%', f'%{filtro}%'))
        else:
            self.cursor.execute("""
                SELECT ig.codigo, ig.nombre, ig.tipo, i.cantidad
                FROM item_general ig
                JOIN inventario i ON ig.id = i.item_id
                WHERE ig.tipo = 'MATERIA PRIMA'
            """)
        return self.cursor.fetchall()
    
    def eliminar_item(self, codigo, tipo):
        self.cursor.execute(
            "DELETE FROM item_general WHERE codigo = ? AND tipo = ?",
            (codigo, tipo)
        )
        self.conn.commit()

    def restar_materia_prima(self, codigo, cantidad_restar):
        self.cursor.execute(
            "SELECT cantidad FROM inventario WHERE item_id = (SELECT id FROM item_general WHERE codigo = ? AND UPPER(tipo) = 'MATERIA PRIMA')",
            (codigo,)
        )
        actual = self.cursor.fetchone()
        actual_cantidad = actual[0] if actual and actual[0] is not None else 0
        if cantidad_restar > actual_cantidad:
            raise ValueError(f"No puede restar más de la cantidad actual ({actual_cantidad}).")
        self.cursor.execute(
            "UPDATE inventario SET cantidad = IFNULL(cantidad,0) - ? WHERE item_id = (SELECT id FROM item_general WHERE codigo = ? AND UPPER(tipo) = 'MATERIA PRIMA')",
            (cantidad_restar, codigo)
        )
        self.conn.commit()