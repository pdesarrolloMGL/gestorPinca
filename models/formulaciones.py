from data.connection import get_connection

class FormulacionesModel:
    def __init__(self):
        self.conn = get_connection()
        self.cursor = self.conn.cursor()

    def obtener_productos(self):
        self.cursor.execute("""
            SELECT ig.id, ig.nombre
            FROM item_general ig
            JOIN item_especifico ie ON ie.item_general_id = ig.id
            JOIN categorias c ON c.id = ie.categoria_id
            ORDER BY ig.nombre
        """)
        return self.cursor.fetchall()

    def obtener_datos_tecnicos(self, prod_id):
        self.cursor.execute("""
            SELECT viscosidad, p_g, color, brillo_60, secado, cubrimiento, molienda, ph, poder_tintoreo
            FROM item_especifico
            WHERE item_general_id = ?
        """, (prod_id,))
        return self.cursor.fetchone()

    def obtener_materias_primas(self, prod_id):
        self.cursor.execute("""
            SELECT mp.codigo, mp.nombre, cp.costo_unitario, f.cantidad, f.unidad
            FROM formulaciones f
            JOIN item_general mp ON f.materia_prima_id = mp.id
            LEFT JOIN costos_produccion cp ON mp.id = cp.item_id
            WHERE f.producto_id = ?
        """, (prod_id,))
        return self.cursor.fetchall()

    def obtener_costos_fijos(self, prod_id):
        self.cursor.execute("""
            SELECT costo_mp_kg, costo_mp_galon, costo_mod, envase, etiqueta, bandeja, plastico
            FROM costos_produccion
            WHERE item_id = ?
        """, (prod_id,))
        return self.cursor.fetchone()

    def obtener_volumen_original(self, prod_id):
        self.cursor.execute("""
            SELECT volumen FROM item_especifico WHERE item_general_id = ?
        """, (prod_id,))
        row = self.cursor.fetchone()
        return float(row[0]) if row and row[0] is not None else None
    
    def get_cantidad_inventario(self, codigo_mp):
        result = self.cursor.execute(
            "SELECT IFNULL(cantidad, 0) FROM inventario WHERE item_id = (SELECT id FROM item_general WHERE codigo = ?)",
            (codigo_mp,)
        ).fetchone()
        return result[0] if result else 0