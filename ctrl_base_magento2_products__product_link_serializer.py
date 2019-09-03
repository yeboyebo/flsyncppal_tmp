from controllers.base.default.serializers.default_serializer import DefaultSerializer


class ProductLinkSerializer(DefaultSerializer):

    def get_data(self):
        return False

        if self.get_init_value("aa.talla") == "TU":
            return False

        self.set_string_value("childSku", self.get_sku())

        return True

    def get_sku(self):
        referencia = self.get_init_value("lsc.idobjeto")
        talla = self.get_init_value("aa.talla")

        if talla == "TU":
            return referencia

        return "{}-{}".format(referencia, talla)
