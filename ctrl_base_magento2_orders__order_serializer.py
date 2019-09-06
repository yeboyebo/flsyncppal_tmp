from YBLEGACY import qsatype
from YBLEGACY.constantes import *

from controllers.base.default.serializers.default_serializer import DefaultSerializer
from controllers.base.magento2.orders.serializers.order_line_serializer import OrderLineSerializer
from controllers.base.magento2.orders.serializers.order_line_shipping_serializer import OrderShippingLineSerializer


class OrderSerializer(DefaultSerializer):

    def get_data(self):
        # cif_nif = self.init_data["cif"]

        # if not cif_nif or cif_nif == "":
        #     raise NameError("No se ha informado el cif")

        # codigo_cliente = qsatype.FLUtil.quickSqlSelect("clientes", "codcliente", "cifnif = '{}'".format(cif_nif))
        # if not codigo_cliente or codigo_cliente == "":
        #     raise NameError("No se encuentra el cliente con el cif {}".format(cif_nif))
        codigo_cliente = "000001"

        codigo_serie = self.get_codserie(codigo_cliente)
        if not codigo_serie:
            raise NameError("No se pudo calcular el código de serie")

        codigo_ejercicio = self.get_codejercicio()
        num_pedido = str(qsatype.FactoriaModulos.get('flfacturac').iface.siguienteNumero(codigo_serie, codigo_ejercicio, "npedidocli"))
        codigo = str(qsatype.FactoriaModulos.get('flfacturac').iface.construirCodigo(codigo_serie, codigo_ejercicio, str(parseInt(num_pedido))))
        self.set_string_value("codserie", codigo_serie)
        self.set_string_value("numero", num_pedido)
        self.set_string_value("codejercicio", codigo_ejercicio)
        self.set_string_value("codigo", codigo, max_characters=15)
        self.set_string_value("codcliente", codigo_cliente)
        # self.set_string_value("codgrupoivaneg", qsatype.FLUtil.quickSqlSelect("clientes", "codgrupoivaneg", "codcliente = '{}'".format(codigo_cliente)))
        self.set_string_relation("fecha", "created_at", max_characters=10)
        self.set_string_relation("fechasalida", "created_at", max_characters=10)
        self.set_string_relation("coddivisa", "currency")
        self.set_string_value("servido", "No")
        self.set_data_value("editable", True)
        # self.set_data_value("egenviado", False)
        self.set_string_value("codalmacen", "ALG")
        self.set_string_value("observaciones", "Pedido: " + self.init_data["increment_id"] + "\nTeléfono: " + self.init_data["shipping_address"]["telephone"])
        self.set_string_value("mg_telefonoenv", self.init_data["shipping_address"]["telephone"])

        shipping_data = self.init_data["shipping_address"]
        firstname = shipping_data["firstname"]
        lastname = shipping_data["lastname"]
        nombre_cliente = str(firstname) + " " + str(lastname)
        street = shipping_data["street"].split("\n")
        direccion = ""
        for i in range(len(street)):
            if direccion == "":
                direccion += str(street[i])
            else:
                direccion += " " + str(street[i])

        city = shipping_data["city"]
        postcode = shipping_data["postcode"]
        region = shipping_data["region"]
        country_id = shipping_data["country_id"]

        self.set_string_relation("cifnif", "cif", max_characters=20, default="-")
        self.set_string_value("nombrecliente", nombre_cliente)
        self.set_string_value("direccion", direccion, max_characters=100)
        self.set_string_value("codpostal", postcode)
        self.set_string_value("ciudad", city)
        self.set_string_value("provincia", region)
        self.set_string_value("codpais", country_id)

        irpf = round(parseFloat(qsatype.FLUtil.quickSqlSelect("series", "irpf", "codserie = '" + codigo_serie + "'")))
        neto = parseFloat(self.init_data["grand_total"]) - parseFloat(self.init_data["tax_amount"])
        self.set_string_value("codpago", self.get_codpago(), max_characters=10)
        self.set_data_value("tasaconv", 1)
        self.set_string_value("irpf", irpf)
        self.set_string_value("totalirpf", (irpf * neto))
        self.set_string_value("neto", neto)
        self.set_data_relation("totaliva", "tax_amount")
        self.set_data_relation("pagado", "grand_total")
        self.set_data_relation("total", "grand_total")
        self.set_string_value("recfinanciero", 0)
        self.set_data_relation("totaleuros", "grand_total")

        if "lines" not in self.data["children"]:
            self.data["children"]["lines"] = []

        for item in self.init_data["items"]:
            item.update({
                "codigo_cliente": codigo_cliente,
                "codigo_serie": codigo_serie
            })
            line_data = OrderLineSerializer().serialize(item)
            self.data["children"]["lines"].append(line_data)

        self.data["children"]["shippingline"] = False
        if parseFloat(self.init_data["shipping_price"]) > 0:
            new_init_data = self.init_data.copy()
            new_init_data.update({
                "codigo_cliente": codigo_cliente,
                "codigo_serie": codigo_serie
            })
            linea_envio = OrderShippingLineSerializer().serialize(new_init_data)
            self.data["children"]["shippingline"] = linea_envio

        return True

    def get_codserie(self, codigo_cliente):
        codigo_serie = False
        if codigo_cliente:
            codigo_serie = qsatype.FLUtil.quickSqlSelect("clientes", "codserie", "codcliente = '{}'".format(codigo_cliente))
        # if not codigo_serie:
        #     codigo_serie = qsatype.FLUtil.quickSqlSelect("tpv_tiendas t INNER JOIN almacenes al ON t.codtienda = al.codtienda", "t.codserie", "al.codalmacen = '{}'".format(qsatype.FactoriaModulos.get('flfacturac').iface.pub_valorDefecto("codalmamayor")), "tpv_tiendas,almacenes")

        return codigo_serie

    def get_codejercicio(self):
        date = self.init_data["created_at"][:10]
        splitted_date = date.split("-")

        return splitted_date[0]

    def get_codpago(self):
        payment_method = self.init_data["payment_method"]
        codpago = qsatype.FLUtil.quickSqlSelect("mg_formaspago", "codpago", "mg_metodopago = '{}'".format(payment_method))
        if not codpago:
            codpago = qsatype.FactoriaModulos.get('flfactppal').iface.pub_valorDefectoEmpresa("codpago")

        return codpago

