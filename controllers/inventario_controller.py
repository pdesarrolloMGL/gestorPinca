from models.inventario import InventarioModel

class InventarioController:
    def __init__(self):
        self.model = InventarioModel()

    def get_productos(self, filtro=None):
        # Para el formulario de facturas - necesita IDs reales
        productos_data = self.model.obtener_productos_con_id(filtro)
        
        # Formato: (id, nombre, descripcion, cantidad, precio, categoria_id)
        productos_formateados = []
        for id_real, codigo, nombre, precio, cantidad in productos_data:
            productos_formateados.append((
                id_real,        # ID real de item_general
                nombre,         # nombre
                codigo,         # descripcion (usando código)
                cantidad,       # cantidad
                precio or 0,    # precio (0 si es None)
                None           # categoria_id
            ))
        
        return productos_formateados

    def obtener_productos(self, filtro=None):
        # Método original para la vista de inventario (sin ID)
        return self.model.obtener_productos(filtro)

    def get_materias_primas(self, filtro=None):
        return self.model.obtener_materias_primas(filtro)

    def add_materia_prima(self, codigo, nombre, cantidad, tipo):
        self.model.agregar_materia_prima(codigo, nombre, cantidad, tipo)

    def delete_item(self, codigo, tipo):
        self.model.eliminar_item(codigo, tipo)

    def restar_materia_prima(self, codigo, cantidad_restar):
        self.model.restar_materia_prima(codigo, cantidad_restar)

    def get_categorias(self):
        return self.model.obtener_categorias()
    
    def crear_item_general(self, nombre, codigo, tipo):
        return self.model.crear_item_general(nombre, codigo, tipo)

    def crear_item_especifico(self, *args, **kwargs):
        return self.model.crear_item_especifico(*args, **kwargs)

    def crear_costos_produccion(self, *args, **kwargs):
        return self.model.crear_costos_produccion(*args, **kwargs)

    def agregar_formulacion(self, producto_id, materia_prima_id, cantidad, unidad=None):
        return self.model.agregar_formulacion(producto_id, materia_prima_id, cantidad, unidad)

    # Métodos adicionales para compatibilidad
    def apartar_materia_prima(self, detalles):
        return self.model.apartar_materia_prima(detalles)

    def devolver_materia_prima(self, detalles):
        return self.model.devolver_materia_prima(detalles)