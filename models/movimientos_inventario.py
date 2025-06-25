from data.connection import get_connection

class MovimientosInventarioModel:
    def __init__(self):
        self.conn = get_connection()
        self.cursor = self.conn.cursor()

    def registrar_movimiento(self, item_id, tipo_movimiento, cantidad, descripcion, referencia_id=None, referencia_tipo=None):
        self.cursor.execute(
            """INSERT INTO movimientos_inventario 
               (item_id, tipo_movimiento, cantidad, descripcion, referencia_id, referencia_tipo) 
               VALUES (?, ?, ?, ?, ?, ?)""",
            (item_id, tipo_movimiento, cantidad, descripcion, referencia_id, referencia_tipo)
        )
        self.conn.commit()
        return self.cursor.lastrowid

    def obtener_movimientos(self, filtro=None, item_id=None):
        query = """
            SELECT m.id, ig.nombre as producto, m.tipo_movimiento, m.cantidad, 
                   m.fecha_movimiento, m.descripcion, m.referencia_id, m.referencia_tipo
            FROM movimientos_inventario m
            JOIN item_general ig ON m.item_id = ig.id
        """
        params = []
        conditions = []

        if item_id:
            conditions.append("m.item_id = ?")
            params.append(item_id)

        if filtro:
            conditions.append("(ig.nombre LIKE ? OR m.descripcion LIKE ?)")
            params.extend([f"%{filtro}%", f"%{filtro}%"])

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY m.fecha_movimiento DESC"
        
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def obtener_estadisticas(self):
        self.cursor.execute("""
            SELECT 
                COALESCE(COUNT(*), 0) as total_movimientos,
                COALESCE(SUM(CASE WHEN tipo_movimiento = 'entrada' THEN cantidad ELSE 0 END), 0) as total_entradas,
                COALESCE(SUM(CASE WHEN tipo_movimiento = 'salida' THEN cantidad ELSE 0 END), 0) as total_salidas
            FROM movimientos_inventario
        """)
        result = self.cursor.fetchone()
        return result if result else (0, 0.0, 0.0)