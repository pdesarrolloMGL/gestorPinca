import sqlite3

conn = sqlite3.connect(r'C:\Users\PDESARROLLO\Documents\gestorPinca\data\pinca.db')
cur = conn.cursor()

datos = [
    {'codigo': 'SAA011', 'nombre': 'DISOLVENTE #3', 'costo_unitario': 4372.0},
    {'codigo': 'SAA022', 'nombre': 'ETANOL 96%', 'costo_unitario': 4400.0},
    {'codigo': 'SAA011', 'nombre': 'DISOLVENTE 2232', 'costo_unitario': 4372.0},
    {'codigo': 'SAA011', 'nombre': 'DISOLVENTE 3', 'costo_unitario': 4372.0},
    {'codigo': 'PE1059', 'nombre': 'PASTA ESMALTE NEGRO', 'costo_unitario': 8105.0},
    {'codigo': 'SOZ016', 'nombre': 'OCTOATO DE ZINC 16%', 'costo_unitario': 16300.0},
    {'codigo': 'PE1010', 'nombre': 'PASTA ESMALTE AMARILLO CROMO MEDIO', 'costo_unitario': 14152.0},
    {'codigo': 'PED010', 'nombre': 'DIOXIDO DE TITANIO SULFATO 2196', 'costo_unitario': 11466.0},
    {'codigo': 'AAS005', 'nombre': 'BENTOCLAY BP184', 'costo_unitario': 17000.0},
    {'codigo': 'PE1021', 'nombre': 'PASTA ESMALTE AZUL 15:3', 'costo_unitario': 11447.0},
    {'codigo': 'ADI010', 'nombre': 'EDAPLAN 918', 'costo_unitario': 22700.0},
    {'codigo': 'ADI010', 'nombre': 'EDAPLAN 918/ LANSPERSE SUV', 'costo_unitario': 22700.0},
    {'codigo': 'ADI010', 'nombre': 'CHEMOSPERSE 77', 'costo_unitario': 22700.0},
    {'codigo': 'PER030', 'nombre': 'PIGMENTO OXIFERR ROJO R-5530', 'costo_unitario': 8000.0}
]

for d in datos:
    # Verifica si ya existe en item_general
    cur.execute(
        "SELECT id FROM item_general WHERE UPPER(TRIM(codigo)) = ? AND UPPER(TRIM(nombre)) = ?",
        (d["codigo"].strip().upper(), d["nombre"].strip().upper())
    )
    row = cur.fetchone()
    if row:
        item_id = row[0]
        print(f"Ya existe: {d['codigo']} | {d['nombre']}")
    else:
        # Inserta en item_general
        cur.execute(
            "INSERT INTO item_general (codigo, nombre, tipo) VALUES (?, ?, ?)",
            (d["codigo"], d["nombre"], "MATERIA PRIMA")
        )
        item_id = cur.lastrowid
        print(f"Insertado en item_general: {d['codigo']} | {d['nombre']}")

    # Verifica si ya existe en item_especifico
    cur.execute(
        "SELECT id FROM item_especifico WHERE item_general_id = ?",
        (item_id,)
    )
    if not cur.fetchone():
        cur.execute(
            "INSERT INTO item_especifico (item_general_id) VALUES (?)",
            (item_id,)
        )
        print(f"Insertado en item_especifico: {item_id}")

    # Verifica si ya existe en costos_produccion
    cur.execute(
        "SELECT id FROM costos_produccion WHERE item_id = ?",
        (item_id,)
    )
    if not cur.fetchone():
        cur.execute(
            "INSERT INTO costos_produccion (item_id, costo_unitario, periodo, metodo_calculo, fecha_calculo) VALUES (?, ?, ?, ?, DATE('now'))",
            (item_id, d["costo_unitario"], '2025-06', 'MANUAL')
        )
        print(f"Insertado en costos_produccion: {item_id}")

conn.commit()
conn.close()