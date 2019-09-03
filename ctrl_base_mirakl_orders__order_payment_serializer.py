from controllers.base.default.serializers.default_serializer import DefaultSerializer


class OrderPaymentSerializer(DefaultSerializer):

    def get_data(self):
        idarqueo = self.get_init_value("idarqueo")
        if not idarqueo:
            return False

        self.set_data_value("anulado", False)
        self.set_data_value("editable", True)
        self.set_data_value("nogenerarasiento", True)

        self.set_string_value("estado", "Pagado")
        self.set_string_value("idtpv_arqueo", idarqueo, max_characters=8)

        self.set_data_relation("importe", "total", default=0)

        self.set_string_relation("fecha", "fecha")
        self.set_string_relation("codtienda", "codtienda")
        self.set_string_relation("codtpv_agente", "codtpv_agente")
        self.set_string_relation("codtpv_puntoventa", "codtpv_puntoventa", max_characters=6)
        self.set_string_relation("codpago", "codpago", max_characters=10)
        self.set_string_relation("codcomanda", "codigo", max_characters=12)

        return True
