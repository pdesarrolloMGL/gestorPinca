from data.connection import get_connection
from datetime import datetime

class FacturasModel:
    def __init__(self):
        self.conn = get_connection()
        self.cursor = self.conn.cursor()

    def obtener_facturas(self, filtro=None):
        query = """
            SELECT f.id, f.numero, c.nombre_encargado || ' / ' || IFNULL(c.nombre_empresa, '') AS cliente, 
                   f.fecha_emision, f.total, f.estado, f.subtotal, f.impuestos, f.cliente_id
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

    # ✅ SOLO ESTOS 3 MÉTODOS PARA NUMERACIÓN AUTOMÁTICA
    def get_ultimo_numero_por_año(self, año):
        """Obtener el último número de factura del año"""
        try:
            query = """
            SELECT numero 
            FROM facturas 
            WHERE numero LIKE ? 
            ORDER BY CAST(SUBSTR(numero, LENGTH(numero) - 3) AS INTEGER) DESC
            LIMIT 1
            """
            patron = f"FAC-{año}-%"
            self.cursor.execute(query, (patron,))
            result = self.cursor.fetchone()
            return result[0] if result else None
        except Exception as e:
            print(f"Error obteniendo último número del año: {e}")
            return None
    
    def existe_numero_factura(self, numero):
        """Verificar si un número de factura ya existe"""
        try:
            query = "SELECT COUNT(*) FROM facturas WHERE numero = ?"
            self.cursor.execute(query, (numero,))
            result = self.cursor.fetchone()
            return result[0] > 0 if result else False
        except Exception as e:
            print(f"Error verificando número: {e}")
            return False

    def generar_numero_automatico(self):
        """Generar número de factura automático"""
        try:
            fecha_actual = datetime.now()
            año = fecha_actual.year
            
            # Buscar el último número del año actual
            ultimo_numero_año = self.get_ultimo_numero_por_año(año)
            
            if ultimo_numero_año:
                # Extraer secuencial del formato FAC-YYYY-NNNN
                partes = ultimo_numero_año.split('-')
                if len(partes) == 3 and partes[-1].isdigit():
                    siguiente_secuencial = int(partes[-1]) + 1
                else:
                    siguiente_secuencial = 1
            else:
                siguiente_secuencial = 1
            
            # Generar y validar que no exista
            max_intentos = 100
            for intento in range(max_intentos):
                numero_propuesto = f"FAC-{año}-{siguiente_secuencial:04d}"
                
                if not self.existe_numero_factura(numero_propuesto):
                    return numero_propuesto
                
                siguiente_secuencial += 1
            
            # Si llegamos aquí, usar timestamp como último recurso
            timestamp = int(datetime.now().timestamp())
            return f"FAC-{timestamp}"
            
        except Exception as e:
            print(f"Error generando número automático: {e}")
            # Número de emergencia
            timestamp = int(datetime.now().timestamp())
            return f"FAC-{timestamp}"
    