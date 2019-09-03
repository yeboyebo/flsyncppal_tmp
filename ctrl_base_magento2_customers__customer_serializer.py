from controllers.base.default.serializers.default_serializer import DefaultSerializer


class CustomerSerializer(DefaultSerializer):

    def get_data(self):

        if str(self.get_init_value("b2b.idclientemagento")) != "" and str(self.get_init_value("b2b.idclientemagento")) != "None":
            self.serializador_actualizar_cliente()
            return True

        nombre_cliente_completo = self.get_nombre_cliente()
        nombre_cliente = nombre_cliente_completo[0]
        apellido_cliente = nombre_cliente_completo[1]

        self.set_string_value("customer//firstname", nombre_cliente)
        self.set_string_value("customer//lastname", apellido_cliente)
        self.set_string_relation("customer//email", "b2b.email")
        self.set_string_relation("customer//taxvat", "c.cifnif")
        self.set_string_relation("customer//store_id", "b2b.idstore")
        self.set_string_relation("customer//group_id", "gcb2b.idgrupoclienteb2b")
        self.set_data_value("customer//website_id", 0)

        nombre_comercial = ""
        if str(self.get_init_value("c.nombrecomercial")) != "None" and str(self.get_init_value("c.nombrecomercial")) != "":
            nombre_comercial = str(self.get_init_value("c.nombrecomercial"))

        direccion = self.get_init_value("dc.dirtipovia") + " " + self.get_init_value("dc.direccion") + " " + self.get_init_value("dc.dirotros") 
        addresses = [
            {"defaultBilling": True,
            "defaultShipping": True,
            "firstname": nombre_cliente,
            "lastname": apellido_cliente,
            "region": {
                "region": self.get_init_value("dc.provincia")
            },
            "countryId": self.get_init_value("dc.codpais"),
            "postcode": self.get_init_value("dc.codpostal"),
            "city": self.get_init_value("dc.ciudad"),
            "street": [direccion],
            "telephone": self.get_init_value("c.telefono1"),
            "vat_id": self.get_init_value("c.cifnif"),
            "company": nombre_comercial}
        ]

        self.set_data_value("customer//addresses", addresses)
        self.set_string_value("password", "A" + str(self.get_init_value("md5(c.cifnif)"))[0:7])

        return True

    def get_nombre_cliente(self):

        nombre_cliente_completo = self.get_init_value("c.nombre").split(" ")
        nombre_cliente = ""
        apellido_cliente = ""
        if len(nombre_cliente_completo) == 1:
            nombre_cliente = nombre_cliente_completo[0]
            apellido_cliente = "-"
        elif len(nombre_cliente_completo) > 1:
            nombre_cliente = nombre_cliente_completo[0]
            for i in range(len(nombre_cliente_completo)):
                if i > 0:
                    if apellido_cliente == "":
                        apellido_cliente += str(nombre_cliente_completo[i])
                    else:
                        apellido_cliente += " " + str(nombre_cliente_completo[i])

        nombre_completo = []
        nombre_completo.append(nombre_cliente)
        nombre_completo.append(apellido_cliente)

        return nombre_completo

    def serializador_actualizar_cliente(self):

        nombre_cliente_completo = self.get_nombre_cliente()
        nombre_cliente = nombre_cliente_completo[0]
        apellido_cliente = nombre_cliente_completo[1]

        self.set_string_relation("customer//id", "b2b.idclientemagento")
        self.set_string_value("customer//firstname", nombre_cliente)
        self.set_string_value("customer//lastname", apellido_cliente)
        self.set_string_relation("customer//email", "b2b.email")
        self.set_string_relation("customer//store_id", "b2b.idstore")
        self.set_string_relation("customer//group_id", "gcb2b.idgrupoclienteb2b")
        self.set_data_value("customer//website_id", 0)

        return True
