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
        
    def calcular_saldo_factura(self, factura_id):
        """Calcula el saldo pendiente de una factura específica"""
        try:
            # ✅ CORREGIR: USAR self.cursor (NO self.controller.cursor)
            query_factura = "SELECT total FROM facturas WHERE id = ?"
            self.cursor.execute(query_factura, (factura_id,))
            resultado_factura = self.cursor.fetchone()
            
            if not resultado_factura:
                return 0.0
                
            total_factura = resultado_factura[0]
            
            # ✅ OBTENER SUMA DE PAGOS DE LA FACTURA
            query_pagos = "SELECT IFNULL(SUM(monto), 0) FROM pagos_cliente WHERE factura_id = ?"
            self.cursor.execute(query_pagos, (factura_id,))
            resultado_pagos = self.cursor.fetchone()
            
            total_pagos = resultado_pagos[0] if resultado_pagos else 0.0
            
            # ✅ CALCULAR SALDO = TOTAL - PAGOS
            saldo = total_factura - total_pagos
            return max(0.0, saldo)  # No permitir saldos negativos
            
        except Exception as e:
            print(f"Error calculando saldo de factura {factura_id}: {e}")
            return 0.0
    
    def obtener_facturas_pendientes(self):
        """Obtener facturas que tienen saldo pendiente"""
        try:
            query = """
                SELECT 
                    f.id, f.numero, f.cliente_id, f.fecha_emision, f.total, f.estado,
                    c.nombre_encargado, c.nombre_empresa,
                    (f.total - IFNULL(SUM(p.monto), 0)) as saldo_pendiente
                FROM facturas f
                LEFT JOIN clientes c ON f.cliente_id = c.id
                LEFT JOIN pagos_cliente p ON f.id = p.factura_id
                GROUP BY f.id, f.numero, f.cliente_id, f.fecha_emision, f.total, f.estado, c.nombre_encargado, c.nombre_empresa
                HAVING saldo_pendiente > 0
                ORDER BY f.fecha_emision DESC
            """
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error obteniendo facturas pendientes: {e}")
            return []

    def obtener_resumen_saldos(self):
        """Obtener resumen de saldos por cliente"""
        try:
            query = """
                SELECT 
                    c.id, c.nombre_encargado, c.nombre_empresa,
                    COUNT(f.id) as total_facturas,
                    SUM(f.total) as total_facturado,
                    IFNULL(SUM(p.monto), 0) as total_pagado,
                    (SUM(f.total) - IFNULL(SUM(p.monto), 0)) as saldo_pendiente
                FROM clientes c
                LEFT JOIN facturas f ON c.id = f.cliente_id
                LEFT JOIN pagos_cliente p ON f.id = p.factura_id
                WHERE f.id IS NOT NULL
                GROUP BY c.id, c.nombre_encargado, c.nombre_empresa
                HAVING saldo_pendiente > 0
                ORDER BY saldo_pendiente DESC
            """
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error obteniendo resumen de saldos: {e}")
            return []
    
    def calcular_saldos_multiples(self, facturas_ids):
        """Calcular saldos de múltiples facturas de una vez"""
        if not facturas_ids:
            return {}
        
        try:
            # Crear placeholders para la consulta IN
            placeholders = ','.join(['?' for _ in facturas_ids])
            
            query = f"""
                SELECT 
                    f.id,
                    f.total,
                    IFNULL(SUM(p.monto), 0) as total_pagado,
                    (f.total - IFNULL(SUM(p.monto), 0)) as saldo
                FROM facturas f
                LEFT JOIN pagos_cliente p ON f.id = p.factura_id
                WHERE f.id IN ({placeholders})
                GROUP BY f.id, f.total
            """
            
            self.cursor.execute(query, facturas_ids)
            resultados = self.cursor.fetchall()
            
            # Convertir a diccionario {factura_id: saldo}
            saldos = {}
            for factura_id, total, total_pagado, saldo in resultados:
                saldos[factura_id] = max(0.0, float(saldo))  # No permitir saldos negativos
            
            return saldos
            
        except Exception as e:
            print(f"Error calculando saldos múltiples: {e}")
            return {}
