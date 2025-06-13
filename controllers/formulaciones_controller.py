from models.formulaciones import FormulacionesModel

class FormulacionesController:
    def __init__(self):
        self.model = FormulacionesModel()

    def get_productos(self):
        return self.model.obtener_productos()

    def get_datos_tecnicos(self, prod_id):
        return self.model.obtener_datos_tecnicos(prod_id)

    def get_materias_primas(self, prod_id):
        return self.model.obtener_materias_primas(prod_id)

    def get_costos_fijos(self, prod_id):
        return self.model.obtener_costos_fijos(prod_id)

    def get_volumen_original(self, prod_id):
        return self.model.obtener_volumen_original(prod_id)