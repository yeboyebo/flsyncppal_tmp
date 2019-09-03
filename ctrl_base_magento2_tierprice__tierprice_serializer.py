from controllers.base.default.serializers.default_serializer import DefaultSerializer


class TierpriceSerializer(DefaultSerializer):

    def get_data(self):
        self.set_string_relation("sku", "lsc.descripcion")
        self.set_data_relation("price", "a.pvp")
        self.set_string_relation("customer_group", "gcb2b.grupoclientesb2b")
        self.set_string_value("price_type", "fixed")
        self.set_data_value("quantity", 1)
        self.set_data_value("website_id", 0)

        return True
