from controllers.base.default.serializers.default_serializer import DefaultSerializer


class InventorySerializer(DefaultSerializer):

    def get_data(self):
        self.set_string_relation("sku", "s.referencia")
        self.set_data_relation("quantity", "s.disponible")
        self.set_string_value("source_code", "default")
        self.set_data_relation("status", "status")
        return True
