import sqlite3

def normaliza(texto):
    return texto.strip().upper() if texto else ""

origen = sqlite3.connect(r'C:\Users\juans\Downloads\gestorPinca\data\pinca.db')
destino = sqlite3.connect(r'C:\Users\juans\Downloads\gestorPinca\data\gestion_pinca.db')

origen_cur = origen.cursor()
destino_cur = destino.cursor()

# Obtén las categorías válidas de la tabla categorias en la nueva base
categorias_validas = set()
for row in destino_cur.execute("SELECT nombre FROM categorias"):
    categorias_validas.add(normaliza(row[0]))

# Trae los datos de productos desde la base de datos origen y normaliza las claves
productos = {}
for row in origen_cur.execute("SELECT codigo, nombre, volumen, costo_unitario, tipo FROM productos"):
    codigo, nombre, volumen, costo_unitario, tipo = row
    if normaliza(tipo) in categorias_validas:
        productos[(normaliza(codigo), normaliza(nombre))] = (
            volumen if volumen is not None else 0,
            costo_unitario if costo_unitario is not None else 0,
            normaliza(tipo)
        )

insertados = 0
for row in destino_cur.execute("""
    SELECT i.id, i.codigo, i.nombre, c.nombre as categoria
    FROM items i
    JOIN categorias c ON i.categoria_id = c.id
    WHERE i.tipo_item = 'PRODUCTO'
    AND i.id NOT IN (SELECT item_id FROM costos_produccion)
"""):
    item_id, codigo, nombre, categoria = row
    datos = productos.get((normaliza(codigo), normaliza(nombre)))
    print(f"Comparando: categoria={normaliza(categoria)} vs tipo_producto={datos[2] if datos else 'N/A'} para {codigo} | {nombre}")
    if datos:
        volumen, costo_unitario, _ = datos
    else:
        volumen, costo_unitario = 0, 0
    print(f"Insertando: {codigo} | {nombre} | categoria: {categoria} | volumen: {volumen} | costo_unitario: {costo_unitario}")
    destino_cur.execute(
        "INSERT INTO costos_produccion (item_id, costo_unitario, volumen, periodo, metodo_calculo, fecha_calculo) VALUES (?, ?, ?, ?, ?, DATE('now'))",
        (item_id, costo_unitario, volumen, '2025-06', 'MANUAL')
    )
    insertados += 1

print(f"Total productos insertados en costos_produccion: {insertados}")

destino.commit()
origen.close()
destino.close()