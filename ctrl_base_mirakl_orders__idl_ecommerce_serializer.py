from YBLEGACY import qsatype

from controllers.base.default.serializers.default_serializer import DefaultSerializer


class IdlEcommerceSerializer(DefaultSerializer):

    def get_data(self):
        self.set_string_relation("codcomanda", "codcomanda", max_characters=15)
        self.set_string_value("tipo", "VENTA")
        self.set_string_value("transportista", "SEUR")
        self.set_string_value("metodoenvioidl", "B2C/STD", skip_replace=True)
        self.set_data_value("imprimiralbaran", False)
        self.set_data_value("imprimirfactura", False)
        self.set_data_value("imprimirdedicatoria", False)
        self.set_data_value("emisor", None)
        self.set_data_value("receptor", None)
        self.set_data_value("mensajededicatoria", None)
        self.set_data_value("esregalo", False)
        self.set_data_value("facturaimpresa", False)
        self.set_data_value("envioidl", False)
        self.set_data_value("eseciweb", True)
        self.set_data_value("numseguimientoinformado", False)
        self.set_string_value("confirmacionenvio", "No")

        return True
