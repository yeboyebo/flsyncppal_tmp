from YBLEGACY import qsatype
from YBLEGACY.constantes import *

from controllers.base.default.serializers.default_serializer import DefaultSerializer


class OrderLineSerializer(DefaultSerializer):

    def get_data(self):
        iva = self.init_data["iva"]
        if not iva or iva == "":
            iva = 0

        if "pvpunitarioiva" not in self.init_data:
            return False

        pvpunitario = parseFloat(self.init_data["pvpunitarioiva"] / ((100 + iva) / 100))
        pvpsindto = parseFloat(self.init_data["pvpsindtoiva"] / ((100 + iva) / 100))
        pvptotal = parseFloat(self.init_data["pvptotaliva"] / ((100 + iva) / 100))

        self.set_string_value("referencia", self.get_referencia(), max_characters=18)
        self.set_string_value("descripcion", self.get_descripcion(), max_characters=100)
        self.set_string_value("barcode", self.get_barcode(), max_characters=20)
        self.set_string_value("talla", self.get_talla(), max_characters=50)
        self.set_string_value("color", self.get_color(), max_characters=50)
        self.set_data_value("cantidad", self.get_cantidad())
        self.set_string_value("codimpuesto", self.get_codimpuesto(self.init_data["codigo_cliente"], self.init_data["codigo_serie"]), max_characters=10)
        self.set_data_value("ivaincluido", True)
        self.set_string_value("dtolineal", 0)
        self.set_string_value("dtopor", 0)
        self.set_string_value("totalenalbaran", 0)
        self.set_data_value("pvpunitario", pvpunitario)
        self.set_data_value("pvpsindto", pvpsindto)
        self.set_data_value("pvptotal", pvptotal)

        self.set_data_relation("iva", "iva")
        self.set_data_relation("pvpunitarioiva", "pvpunitarioiva")
        self.set_data_relation("pvpsindtoiva", "pvpsindtoiva")
        self.set_data_relation("pvptotaliva", "pvptotaliva")

        return True

    def get_splitted_sku(self):
        return self.init_data["sku"].split("-")

    def get_referencia(self):
        return self.get_splitted_sku()[0]

    def get_descripcion(self):
        return qsatype.FLUtil.quickSqlSelect("articulos", "descripcion", "referencia = '{}'".format(self.get_referencia()))

    def get_barcode(self):
        splitted_sku = self.get_splitted_sku()

        if len(splitted_sku) == 1:
            referencia = splitted_sku[0].upper()
            return qsatype.FLUtil.quickSqlSelect("atributosarticulos", "barcode", "UPPER(referencia) = '{}'".format(referencia))
        elif len(splitted_sku) == 2:
            referencia = splitted_sku[0].upper()
            talla = splitted_sku[1]
            return qsatype.FLUtil.quickSqlSelect("atributosarticulos", "barcode", "UPPER(referencia) = '{}' AND talla = '{}'".format(referencia, talla))
        else:
            return "ERRORNOTALLA"

    def get_talla(self):
        splitted_sku = self.get_splitted_sku()

        if len(splitted_sku) == 1:
            referencia = splitted_sku[0]
            return qsatype.FLUtil.quickSqlSelect("atributosarticulos", "talla", "referencia = '{}'".format(referencia))
        elif len(splitted_sku) == 2:
            return splitted_sku[1]
        else:
            return "TU"

    def get_color(self):
        splitted_sku = self.get_splitted_sku()

        if len(splitted_sku) == 1:
            referencia = splitted_sku[0]
            return qsatype.FLUtil.quickSqlSelect("atributosarticulos", "color", "referencia = '{}'".format(referencia))
        elif len(splitted_sku) == 2:
            referencia = splitted_sku[0]
            talla = splitted_sku[1]
            return qsatype.FLUtil.quickSqlSelect("atributosarticulos", "color", "referencia = '{}' AND talla = '{}'".format(referencia, talla))
        else:
            return "U"

    def get_codimpuesto(self, codigo_cliente, codigo_serie):
        codimpuesto = False
        if codigo_cliente:
            codimpuesto = qsatype.FLUtil.quickSqlSelect("gruposcontablesivaneg INNER JOIN clientes ON gruposcontablesivaneg.codgrupoivaneg = clientes.codgrupoivaneg", "gruposcontablesivaneg.codimpuestodefecto", "clientes.codcliente = '{}'".format(codigo_cliente), "gruposcontablesivaneg,clientes")
            print(codimpuesto)

        if not codimpuesto:
            codimpuesto = qsatype.FLUtil.quickSqlSelect("series", "codimpuesto", "codserie = '{}'".format(codigo_serie))

        if not codimpuesto:
            codimpuesto = qsatype.FLUtil.quickSqlSelect("articulos", "codimpuesto", "referencia = '{}'".format(self.get_referencia()))

        if not codimpuesto:
            codimpuesto = "GEN"

        return codimpuesto

    def get_cantidad(self):
        return self.init_data["cantidad"]
