from controllers.base.default.serializers.default_serializer import DefaultSerializer


class OrderShippingLineSerializer(DefaultSerializer):

    def get_data(self):
        # street = self.init_data["shipping_address"]["street"].split("\n")
        # dirtipoviaenv = street[0] if len(street) >= 1 else ""
        # direccionenv = street[1] if len(street) >= 2 else ""
        # dirnumenv = street[2] if len(street) >= 3 else ""
        # dirotrosenv = street[3] if len(street) >= 4 else ""

        self.set_string_relation("mg_direccionenv", "customer//shipping_address//street_1", max_characters=200)
        # self.set_string_value("mg_dirtipoviaenv", dirtipoviaenv, max_characters=100)
        # self.set_string_value("mg_dirnumenv", dirnumenv, max_characters=100)
        # self.set_string_value("mg_dirotrosenv", dirotrosenv, max_characters=100)

        self.set_string_relation("mg_numseguimiento", "shipping_tracking", max_characters=100)
        self.set_string_relation("mg_numcliente", "customer//customer_id", max_characters=15)
        # self.set_string_relation("mg_email", "email", max_characters=200)
        self.set_string_value("mg_metodopago", "TARJ", max_characters=30)
        self.set_string_relation("mg_metodoenvio", "shipping_type_label", max_characters=500)

        # self.set_data_relation("mg_unidadesenv", "units")
        self.set_data_relation("mg_gastosenv", "shipping_price")

        self.set_string_relation("mg_nombreenv", "customer//shipping_address//firstname", max_characters=100)
        self.set_string_relation("mg_apellidosenv", "customer//shipping_address//lastname", max_characters=200)
        self.set_string_relation("mg_codpostalenv", "customer//shipping_address//zip_code", max_characters=10)
        self.set_string_relation("mg_ciudadenv", "customer//shipping_address//city", max_characters=100)
        self.set_string_value("mg_paisenv", "ES")
        self.set_string_relation("mg_telefonoenv", "customer//shipping_address//phone", max_characters=30)

        self.set_data_value("mg_confac", False)

        return True
