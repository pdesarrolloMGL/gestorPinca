import sqlite3
from datetime import datetime

# Conexión a la base de datos nueva
conn_new = sqlite3.connect(r'C:\Users\PDESARROLLO\Documents\gestorPinca\data\pinca.db')
cur_new = conn_new.cursor()

# Fecha actual en formato YYYY-MM-DD
fecha_actual = datetime.now().strftime('%Y-%m-%d')

# Inserta todos los items de item_general en inventario con cantidad y fecha_actualiz vacíos o actuales
cur_new.execute("SELECT id FROM item_general")
item_ids = cur_new.fetchall()

for (item_id,) in item_ids:
    cur_new.execute(
        "INSERT INTO inventario (item_id, cantidad, fecha_update) VALUES (?, ?, ?)",
        (item_id, None, fecha_actual)
    )

conn_new.commit()
conn_new.close()