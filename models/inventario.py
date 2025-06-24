from data.connection import get_connection

class InventarioModel:
    def __init__(self):
        self.conn = get_connection()
        self.cursor = self.conn.cursor()
        
    def obtener_productos(self, filtro=None):
        query = """
            SELECT ig.codigo, ig.nombre, IFNULL(cp.costo_unitario, 0), IFNULL(inv.cantidad, 0)
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
        query = """
            SELECT ig.codigo, ig.nombre, IFNULL(cp.costo_unitario, 0), IFNULL(i.cantidad, 0)
            FROM item_general ig
            JOIN inventario i ON ig.id = i.item_id
            LEFT JOIN costos_produccion cp ON ig.id = cp.item_id
            WHERE UPPER(ig.tipo) = 'MATERIA PRIMA'
        """
        params = ()
        if filtro:
            query += " AND (lower(ig.codigo) LIKE ? OR lower(ig.nombre) LIKE ?)"
            params = (f"%{filtro}%", f"%{filtro}%")
        self.cursor.execute(query, params)
        return self.cursor.fetchall()
    
    def eliminar_item(self, codigo, tipo):
        # Obtener el id del producto o materia prima
        self.cursor.execute("SELECT id FROM item_general WHERE codigo = ? AND tipo = ?", (codigo, tipo))
        row = self.cursor.fetchone()
        if row:
            item_id = row[0]
            # Borra formulaciones y costos_produccion relacionados
            self.cursor.execute("DELETE FROM formulaciones WHERE producto_id = ?", (item_id,))
            self.cursor.execute("DELETE FROM costos_produccion WHERE item_id = ?", (item_id,))
            self.cursor.execute("DELETE FROM inventario WHERE item_id = ?", (item_id,))
            self.cursor.execute("DELETE FROM item_especifico WHERE item_general_id = ?", (item_id,))
            self.cursor.execute("DELETE FROM item_general WHERE id = ?", (item_id,))
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

    def crear_item_general(self, nombre, codigo, tipo):
        self.cursor.execute(
            "INSERT INTO item_general (nombre, codigo, tipo) VALUES (?, ?, ?)",
            (nombre, codigo, tipo)
        )
        self.conn.commit()
        return self.cursor.lastrowid

    def crear_item_especifico(self, item_general_id, viscosidad, p_g, color, brillo_60, secado, cubrimiento, molienda, ph, poder_tintoreo, volumen, categoria_id):
        self.cursor.execute(
            "INSERT INTO item_especifico (item_general_id, viscosidad, p_g, color, brillo_60, secado, cubrimiento, molienda, ph, poder_tintoreo, volumen, categoria_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (item_general_id, viscosidad, p_g, color, brillo_60, secado, cubrimiento, molienda, ph, poder_tintoreo, volumen, categoria_id)
        )
        self.conn.commit()

    def crear_costos_produccion(self, item_id, envase, etiqueta, bandeja, plastico, volumen):
        self.cursor.execute(
            "INSERT INTO costos_produccion (item_id, envase, etiqueta, bandeja, plastico, volumen, periodo, fecha_calculo) VALUES (?, ?, ?, ?, ?, ?, strftime('%Y-%m', 'now'), date('now'))",
            (item_id, envase, etiqueta, bandeja, plastico, volumen)
        )
        self.conn.commit()

    def agregar_formulacion(self, producto_id, materia_prima_id, cantidad, unidad=None):
        self.cursor.execute(
            "INSERT INTO formulaciones (producto_id, materia_prima_id, cantidad, unidad) VALUES (?, ?, ?, ?)",
            (producto_id, materia_prima_id, cantidad, unidad)
        )
        self.conn.commit()
    
    def obtener_categorias(self):
        self.cursor.execute("SELECT id, nombre FROM categorias")
        return self.cursor.fetchall()

    def apartar_materia_prima(self, detalles):
        for d in detalles:
            self.cursor.execute(
                "UPDATE inventario SET cantidad = cantidad - ? WHERE item_id = (SELECT id FROM item_general WHERE codigo = ?)",
                (d['cantidad_necesaria'], d['codigo'])
            )
        self.conn.commit()

    def devolver_materia_prima(self, detalles):
        for d in detalles:
            self.cursor.execute(
                "UPDATE inventario SET cantidad = cantidad + ? WHERE item_id = (SELECT id FROM item_general WHERE codigo = ?)",
                (d['cantidad_necesaria'], d['codigo'])
            )
        self.conn.commit()