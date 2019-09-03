from YBLEGACY import qsatype
from YBLEGACY.constantes import *

from controllers.base.default.serializers.default_serializer import DefaultSerializer


class VentaseciwebSerializer(DefaultSerializer):

    def get_data(self):
        billing = self.get_init_value("customer//billing_address")

        if not billing:
            if qsatype.FLUtil.sqlSelect("ew_ventaseciweb", "idweb", "idweb = '{}'".format(self.get_init_value("order_id"))):
                return False

            now = str(qsatype.Date())

            self.set_string_relation("idweb", "order_id")
            self.set_string_value("estado", "WAITING_ACCEPTANCE")
            self.set_string_value("datosventa", self.init_data, max_characters=None, skip_replace=True)
            self.set_data_value("aceptado", False)
            self.set_data_value("idtpv_comanda", None)
            self.set_data_value("infoclienterecibida", False)
            self.set_data_value("trakinginformado", False)
            self.set_data_value("envioinformado", False)
            self.set_data_value("fechaentregainformada", False)
            self.set_string_value("fechaalta", now[:10])
            self.set_string_value("horaalta", now[-8:])
        else:
            if qsatype.FLUtil.sqlSelect("ew_ventaseciweb", "datosenvio", "idweb = '{}'".format(self.get_init_value("order_id"))) and not qsatype.FLUtil.sqlSelect("ew_ventaseciweb", "idtpv_comanda", "idweb = '{}'".format(self.get_init_value("order_id"))):
                return False

            self.set_string_relation("idweb", "order_id")
            self.set_string_value("estado", "SHIPPING")
            self.set_string_value("datosenvio", self.init_data, max_characters=None, skip_replace=True)
            self.set_data_value("infoclienterecibida", True)
            self.set_data_relation("idtpv_comanda", "idtpv_comanda")
       
        return True
