from YBLEGACY import qsatype
from YBLEGACY.constantes import *

from controllers.base.default.serializers.default_serializer import DefaultSerializer


class DevolucioneseciwebSerializer(DefaultSerializer):

    def get_data(self):
        now = str(qsatype.Date())

        self.set_string_relation("idventaweb", "order_id")
        self.set_string_value("estado", "PENDIENTE")
        self.set_string_value("datosdevol", self.init_data["body"], max_characters=None, skip_replace=True)
        self.set_data_value("recibida", False)
        self.set_string_value("fechaalta", now[:10])
        self.set_string_value("horaalta", now[-8:])
        self.set_string_relation("date_created", "date_created")
        self.set_string_relation("valdemoro", "valdemoro")

        return True
