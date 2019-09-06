from YBLEGACY import qsatype
from YBLEGACY.constantes import *

from controllers.base.default.serializers.default_serializer import DefaultSerializer


class OrderShippingLineSerializer(DefaultSerializer):

    def get_data(self):
        pvpunitarioiva = self.init_data["shipping_price"]
        self.set_string_value("referencia", "art1")
        self.set_string_value("descripcion", "Gastos de envío")
        # self.set_string_value("barcode", "8433613403654")
        # self.set_string_value("talla", "TU")
        # self.set_string_value("color", "U")
        self.set_data_value("cantidad", 1)
        self.set_string_value("codimpuesto", self.get_codimpuesto(self.init_data["codigo_cliente"], self.init_data["codigo_serie"]), max_characters=10)
        self.set_data_value("ivaincluido", True)
        self.set_string_value("iva", 0)
        self.set_string_value("dtolineal", 0)
        self.set_string_value("dtopor", 0)
        self.set_string_value("totalenalbaran", 0)
        self.set_string_value("pvpunitario", pvpunitarioiva)
        self.set_string_value("pvpsindto", pvpunitarioiva)
        self.set_string_value("pvptotal", pvpunitarioiva)
        self.set_string_value("pvpunitarioiva", pvpunitarioiva)
        self.set_string_value("pvpsindtoiva", pvpunitarioiva)
        self.set_string_value("pvptotaliva", pvpunitarioiva)
        return True

    def get_codimpuesto(self, codigo_cliente, codigo_serie):
        codimpuesto = False
        # if codigo_cliente:
        #     codimpuesto = qsatype.FLUtil.quickSqlSelect("gruposcontablesivaneg INNER JOIN clientes ON gruposcontablesivaneg.codgrupoivaneg = clientes.codgrupoivaneg", "gruposcontablesivaneg.codimpuestodefecto", "clientes.codcliente = '{}'".format(codigo_cliente), "gruposcontablesivaneg,clientes")
        #     print(codimpuesto)

        # if not codimpuesto:
        #     codimpuesto = qsatype.FLUtil.quickSqlSelect("series", "codimpuesto", "codserie = '{}'".format(codigo_serie))

        # if not codimpuesto:
        #     codimpuesto = qsatype.FLUtil.quickSqlSelect("articulos", "codimpuesto", "referencia = '{}'".format(self.get_referencia()))

        if not codimpuesto:
            codimpuesto = "GEN"

        return codimpuesto

