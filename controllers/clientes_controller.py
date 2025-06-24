from models.clientes import ClientesModel

class ClientesController:
    def __init__(self):
        self.model = ClientesModel()

    def get_clientes(self, filtro=None):
        return self.model.obtener_clientes(filtro)

    def agregar_cliente(self, nombre, tipo_documento, numero_documento, direccion, telefono, email):
        return self.model.agregar_cliente(nombre, tipo_documento, numero_documento, direccion, telefono, email)

    def eliminar_cliente(self, cliente_id):
        self.model.eliminar_cliente(cliente_id)

    def get_facturas_cliente(self, cliente_id):
        return self.model.get_facturas_cliente(cliente_id)
