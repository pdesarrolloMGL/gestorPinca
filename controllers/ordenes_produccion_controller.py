from models.ordenes_produccion import OrdenesProduccionModel

class OrdenesProduccionController:
    def __init__(self):
        self.model = OrdenesProduccionModel()

    def get_productos(self):
        return self.model.obtener_productos()

    def get_ordenes(self):
        return self.model.obtener_ordenes()

    def get_detalle_orden(self, orden_id):
        return self.model.obtener_materias_primas_orden(orden_id)

    def puede_producir(self, producto_id, cantidad_a_producir):
        return self.model.puede_producir(producto_id, cantidad_a_producir)

    def get_product_id_by_name(self, nombre):
        return self.model.obtener_id_producto_por_nombre(nombre)

    def actualizar_estado_orden(self, orden_id, nuevo_estado):
        self.model.actualizar_estado_orden(orden_id, nuevo_estado)

    def actualizar_observaciones_orden(self, orden_id, nueva_desc):
        self.model.actualizar_observaciones_orden(orden_id, nueva_desc)

    def actualizar_fecha_fin_orden(self, orden_id, nueva_fecha):
        self.model.actualizar_fecha_fin_orden(orden_id, nueva_fecha)

    def get_detalle_orden_virtual(self, producto_id, cantidad):
        return self.model.obtener_materias_primas_virtual(producto_id, cantidad)

    def devolver_materia_prima_por_orden(self, orden_id):
        self.model.devolver_materia_prima_por_orden(orden_id)

    def procesar_creacion_orden(self, producto_id, cantidad, observaciones=""):
        return self.model.procesar_creacion_orden(producto_id, cantidad, observaciones)

    def eliminar_orden(self, orden_id):
        self.model.eliminar_orden(orden_id)