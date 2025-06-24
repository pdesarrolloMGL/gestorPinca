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
        self.cursor.execute("SELECT item_id, cantidad_producida FROM ordenes_produccion WHERE id = ?", (orden_id,))
        row = self.cursor.fetchone()
        if not row:
            return []
        producto_id, cantidad_producida = row

        self.cursor.execute("SELECT volumen FROM item_especifico WHERE item_general_id = ?", (producto_id,))
        row = self.cursor.fetchone()
        volumen_base = float(row[0]) if row and row[0] is not None else 1

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
            cantidad_necesaria = round(float(cantidad_base) * (cantidad_producida / volumen_base), 2)
            resultado.append({
                "id": mp_id,
                "codigo": codigo,
                "nombre": nombre,
                "cantidad_necesaria": cantidad_necesaria,
                "unidad": unidad,
                "costo_unitario": round(costo_unitario, 2)
            })
        return resultado

    def puede_producir(self, producto_id, cantidad_a_producir):
        self.cursor.execute("""
            SELECT mp.id, mp.codigo, mp.nombre, f.cantidad, f.unidad
            FROM formulaciones f
            JOIN item_general mp ON f.materia_prima_id = mp.id
            WHERE f.producto_id = ?
        """, (producto_id,))
        materias = self.cursor.fetchall()

        self.cursor.execute("SELECT volumen FROM item_especifico WHERE item_general_id = ?", (producto_id,))
        row = self.cursor.fetchone()
        volumen_base = float(row[0]) if row and row[0] is not None else 1

        faltantes = []
        for mp_id, codigo, nombre, cantidad_base, unidad in materias:
            cantidad_necesaria = round(float(cantidad_base) * (cantidad_a_producir / volumen_base), 2)
            self.cursor.execute("SELECT IFNULL(cantidad, 0) - IFNULL(apartada, 0) FROM inventario WHERE item_id = ?", (mp_id,))
            cantidad_inventario = round(self.cursor.fetchone()[0], 2)
            if cantidad_inventario < cantidad_necesaria:
                faltantes.append({
                    "codigo": codigo,
                    "nombre": nombre,
                    "necesaria": cantidad_necesaria,
                    "en_stock": cantidad_inventario
                })
        return faltantes

    def obtener_id_producto_por_nombre(self, nombre):
        self.cursor.execute("SELECT id FROM item_general WHERE nombre = ?", (nombre,))
        row = self.cursor.fetchone()
        return row[0] if row else None

    def get_cantidad_inventario(self, codigo_mp):
        result = self.cursor.execute(
            "SELECT IFNULL(cantidad, 0) FROM inventario WHERE item_id = (SELECT id FROM item_general WHERE codigo = ?)",
            (codigo_mp,)
        ).fetchone()
        return round(float(result[0]), 2) if result else 0

    def actualizar_estado_orden(self, orden_id, nuevo_estado):
        self.cursor.execute("UPDATE ordenes_produccion SET estado = ? WHERE id = ?", (nuevo_estado, orden_id))
        self.conn.commit()

    def actualizar_observaciones_orden(self, orden_id, nueva_desc):
        self.cursor.execute("UPDATE ordenes_produccion SET observaciones = ? WHERE id = ?", (nueva_desc, orden_id))
        self.conn.commit()

    def actualizar_fecha_fin_orden(self, orden_id, nueva_fecha):
        self.cursor.execute("UPDATE ordenes_produccion SET fecha_fin = ? WHERE id = ?", (nueva_fecha, orden_id))
        self.conn.commit()

    def obtener_materias_primas_virtual(self, producto_id, cantidad):
        self.cursor.execute("""
            SELECT mp.codigo, mp.nombre, cp.costo_unitario, f.cantidad, f.unidad
            FROM formulaciones f
            JOIN item_general mp ON f.materia_prima_id = mp.id
            LEFT JOIN costos_produccion cp ON mp.id = cp.item_id
            WHERE f.producto_id = ?
        """, (producto_id,))
        materias = self.cursor.fetchall()
        self.cursor.execute("SELECT volumen FROM item_especifico WHERE item_general_id = ?", (producto_id,))
        row_vol = self.cursor.fetchone()
        volumen_base = float(row_vol[0]) if row_vol and row_vol[0] is not None else 1

        factor = float(cantidad) / volumen_base if volumen_base else 1

        detalles = []
        for codigo, nombre, costo_unitario, cantidad_base, unidad in materias:
            cantidad_necesaria = round(float(cantidad_base) * factor, 2)
            detalles.append({
                "codigo": codigo,
                "nombre": nombre,
                "costo_unitario": round(costo_unitario, 2) if costo_unitario else 0,
                "cantidad_necesaria": cantidad_necesaria,
                "unidad": unidad
            })
        return detalles

    def agregar_detalle_orden(self, orden_id, item_id, cantidad_utilizada):
        self.cursor.execute(
            "INSERT INTO detalle_orden_produccion (orden_id, item_id, cantidad_utilizada) VALUES (?, ?, ?)",
            (orden_id, item_id, round(cantidad_utilizada, 2))
        )
        self.conn.commit()

    def obtener_id_item_por_codigo(self, codigo):
        self.cursor.execute("SELECT id FROM item_general WHERE codigo = ?", (codigo,))
        row = self.cursor.fetchone()
        return row[0] if row else None

    def procesar_creacion_orden(self, producto_id, cantidad, observaciones):
        orden_id = self.crear_orden(producto_id, cantidad, observaciones)
        detalles = self.obtener_materias_primas_virtual(producto_id, cantidad)

        suficientes = True
        for d in detalles:
            cantidad_en_inventario = self.get_cantidad_inventario(d["codigo"])
            if cantidad_en_inventario < d["cantidad_necesaria"]:
                suficientes = False
                break

        if suficientes:
            self.actualizar_estado_orden(orden_id, "CONFIRMADA")
            for d in detalles:
                item_id = self.obtener_id_item_por_codigo(d["codigo"])
                self.agregar_detalle_orden(orden_id, item_id, d["cantidad_necesaria"])
            for d in detalles:
                item_id = self.obtener_id_item_por_codigo(d["codigo"])
                cantidad_a_reservar = d["cantidad_necesaria"]
                self.cursor.execute(
                    "UPDATE inventario SET apartada = apartada + ? WHERE item_id = ?",
                    (round(cantidad_a_reservar, 2), item_id)
                )
            self.conn.commit()
            return orden_id
        else:
            self.actualizar_estado_orden(orden_id, "PENDIENTE")
            return None

    def devolver_materia_prima_por_orden(self, orden_id):
        self.cursor.execute("""
            SELECT item_id, cantidad_utilizada
            FROM detalle_orden_produccion
            WHERE orden_id = ?
        """, (orden_id,))
        detalles = self.cursor.fetchall()
        for item_id, cantidad in detalles:
            self.cursor.execute(
                "UPDATE inventario SET apartada = apartada - ? WHERE item_id = ?",
                (round(cantidad, 2), item_id)
            )
        self.conn.commit()

    def eliminar_orden(self, orden_id):
        # Borra detalles primero por integridad referencial
        self.cursor.execute("DELETE FROM detalle_orden_produccion WHERE orden_id = ?", (orden_id,))
        self.cursor.execute("DELETE FROM ordenes_produccion WHERE id = ?", (orden_id,))
        self.conn.commit()