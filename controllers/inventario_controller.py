from models.inventario import InventarioModel

class InventarioController:
    def __init__(self):
        self.model = InventarioModel()

    def get_productos(self, filtro=None):
        return self.model.obtener_productos(filtro)

    def get_materias_primas(self, filtro=None):
        return self.model.obtener_materias_primas(filtro)

    def add_materia_prima(self, codigo, nombre, cantidad, tipo):
        self.model.agregar_materia_prima(codigo, nombre, cantidad, tipo)

    def delete_item(self, codigo, tipo):
        self.model.eliminar_item(codigo, tipo)

    def restar_materia_prima(self, codigo, cantidad_restar):
        self.model.restar_materia_prima(codigo, cantidad_restar)