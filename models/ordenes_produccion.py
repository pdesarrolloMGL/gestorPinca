from data.connection import get_connection
import datetime

class OrdenesProduccionModel:
    def __init__(self):
        self.conn = get_connection()
        self.cursor = self.conn.cursor()

    def obtener_productos(self, filtro=None):
        query = """
            SELECT ig.id, ig.nombre, IFNULL(cp.costo_unitario, 0), IFNULL(inv.cantidad, 0)
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

    def crear_orden(self, producto_id, cantidad, observaciones=""):
        codigo = f"OP-{int(datetime.datetime.now().timestamp())}"
        fecha_inicio = datetime.datetime.now()
        estado = "PENDIENTE"
        self.cursor.execute(
            "INSERT INTO ordenes_produccion (codigo, item_id, cantidad_producida, fecha_inicio, estado, observaciones) VALUES (?, ?, ?, ?, ?, ?)",
            (codigo, producto_id, cantidad, fecha_inicio, estado, observaciones)
        )
        self.conn.commit()
        return self.cursor.lastrowid

    def obtener_ordenes(self):
        self.cursor.execute("""
            SELECT o.id, o.codigo, ig.nombre, o.cantidad_producida, o.observaciones, o.estado, o.fecha_fin
            FROM ordenes_produccion o
            JOIN item_general ig ON o.item_id = ig.id
            ORDER BY o.id DESC
        """)
        return self.cursor.fetchall()

    def obtener_materias_primas_orden(self, orden_id):
        # Obtener producto y cantidad de la orden
        self.cursor.execute("SELECT item_id, cantidad_producida FROM ordenes_produccion WHERE id = ?", (orden_id,))
        row = self.cursor.fetchone()
        if not row:
            return []
        producto_id, cantidad_producida = row

        # Obtener volumen base del producto
        self.cursor.execute("SELECT volumen FROM item_especifico WHERE item_general_id = ?", (producto_id,))
        row = self.cursor.fetchone()
        volumen_base = float(row[0]) if row and row[0] is not None else 1

        # Obtener materias primas, cantidades necesarias y costo unitario
        self.cursor.execute("""
            SELECT mp.id, mp.codigo, mp.nombre, f.cantidad, f.unidad, IFNULL(cp.costo_unitario, 0)
            FROM formulaciones f
            JOIN item_general mp ON f.materia_prima_id = mp.id
            LEFT JOIN costos_produccion cp ON mp.id = cp.item_id
            WHERE f.producto_id = ?
        """, (producto_id,))
        materias = self.cursor.fetchall()

        resultado = []
        for mp_id, codigo, nombre, cantidad_base, unidad, costo_unitario in materias:
            cantidad_necesaria = float(cantidad_base) * (cantidad_producida / volumen_base)
            resultado.append({
                "id": mp_id,
                "codigo": codigo,
                "nombre": nombre,
                "cantidad_necesaria": cantidad_necesaria,
                "unidad": unidad,
                "costo_unitario": costo_unitario
            })
        return resultado

    def puede_producir(self, producto_id, cantidad_a_producir):
        # 1. Obtener la formulación del producto
        self.cursor.execute("""
            SELECT mp.id, mp.codigo, mp.nombre, f.cantidad, f.unidad
            FROM formulaciones f
            JOIN item_general mp ON f.materia_prima_id = mp.id
            WHERE f.producto_id = ?
        """, (producto_id,))
        materias = self.cursor.fetchall()

        # 2. Obtener el volumen base del producto
        self.cursor.execute("SELECT volumen FROM item_especifico WHERE item_general_id = ?", (producto_id,))
        row = self.cursor.fetchone()
        volumen_base = float(row[0]) if row and row[0] is not None else 1

        # 3. Verificar inventario para cada materia prima
        faltantes = []
        for mp_id, codigo, nombre, cantidad_base, unidad in materias:
            cantidad_necesaria = float(cantidad_base) * (cantidad_a_producir / volumen_base)
            self.cursor.execute("SELECT IFNULL(cantidad, 0) FROM inventario WHERE item_id = ?", (mp_id,))
            cantidad_inventario = self.cursor.fetchone()[0]
            if cantidad_inventario < cantidad_necesaria:
                faltantes.append({
                    "codigo": codigo,
                    "nombre": nombre,
                    "necesaria": cantidad_necesaria,
                    "en_stock": cantidad_inventario
                })
        return faltantes  # Lista vacía si se puede producir, si no, lista de faltantes

    def obtener_id_producto_por_nombre(self, nombre):
        self.cursor.execute("SELECT id FROM item_general WHERE nombre = ?", (nombre,))
        row = self.cursor.fetchone()
        return row[0] if row else None
    
    def get_cantidad_inventario(self, codigo_mp):
        result = self.cursor.execute(
            "SELECT IFNULL(cantidad, 0) FROM inventario WHERE item_id = (SELECT id FROM item_general WHERE codigo = ?)",
            (codigo_mp,)
        ).fetchone()
        return float(result[0]) if result else 0

    def get_tipo_producto(self, producto_id):
        self.cursor.execute("SELECT unidad FROM item_especifico WHERE item_general_id = ?", (producto_id,))
        row = self.cursor.fetchone()
        return row[0] if row else "galon"

    def actualizar_estado_orden(self, orden_id, nuevo_estado):
        cursor = self.cursor
        cursor.execute("UPDATE ordenes_produccion SET estado = ? WHERE id = ?", (nuevo_estado, orden_id))
        self.conn.commit()

    def actualizar_observaciones_orden(self, orden_id, nueva_desc):
        cursor = self.cursor
        cursor.execute("UPDATE ordenes_produccion SET observaciones = ? WHERE id = ?", (nueva_desc, orden_id))
        self.conn.commit()

    def actualizar_fecha_fin_orden(self, orden_id, nueva_fecha):
        cursor = self.cursor
        cursor.execute("UPDATE ordenes_produccion SET fecha_fin = ? WHERE id = ?", (nueva_fecha, orden_id))
        self.conn.commit()