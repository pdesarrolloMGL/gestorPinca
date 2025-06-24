from models.pagos_cliente import PagosClienteModel

class PagosClienteController:
    def __init__(self):
        self.model = PagosClienteModel()

    def registrar_pago(self, cliente_id, factura_id, monto, metodo_pago, observaciones):
        return self.model.registrar_pago(cliente_id, factura_id, monto, metodo_pago, observaciones)

    def obtener_pagos_cliente(self, cliente_id):
        return self.model.obtener_pagos_cliente(cliente_id)

    def total_pagado(self, cliente_id):
        return self.model.total_pagado(cliente_id)

    def total_facturado(self, cliente_id):
        return self.model.total_facturado(cliente_id)

    def saldo_cliente(self, cliente_id):
        return self.model.saldo_cliente(cliente_id)

    def total_pagado_factura(self, factura_id):
        return self.model.total_pagado_factura(factura_id)

    def get_historial_pagos_cliente(self, cliente_id):
        return self.model.get_historial_pagos_cliente(cliente_id)
