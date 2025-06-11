def limpiar_celdas_widget(table):
    for i in range(table.rowCount()):
        for j in range(table.columnCount()):
            widget = table.cellWidget(i, j)
            if widget is not None:
                table.removeCellWidget(i, j)

def formatear_moneda(valor):
    try:
        return "$ {:,.2f}".format(float(valor))
    except Exception:
        return str(valor)