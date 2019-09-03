import requests
import json
from abc import ABC

from YBLEGACY import qsatype

from controllers.base.magento2.drivers.magento2 import Magento2Driver
from controllers.base.default.controllers.upload_sync import UploadSync

from controllers.base.magento2.inventory.serializers.inventory_serializer import InventorySerializer


class InventoryUpload(UploadSync, ABC):

    inventory_url = "<host>/rest/default/V1/inventory/source-items"
    inventory_test_url = "<testhost>/rest/default/V1/inventory/source-items"

    idlinea = None
    idsincro = None
    referencia = None

    def __init__(self, process_name, params=None):
        super().__init__(process_name, Magento2Driver(), params)

    def get_data(self):
        data = self.get_db_data()

        if data == []:
            return data

        inventory = self.get_inventory_serializer().serialize(data[0])
        if not inventory:
            return inventory

        del inventory["children"]
        return {
            "sourceItems": [inventory]
        }

    def get_db_data(self):
        body = []

        q = qsatype.FLSqlQuery()
        q.setSelect("s.referencia, s.talla, s.disponible, lsc.idobjeto")
        q.setFrom("lineassincro_catalogo lsc INNER JOIN stocks s ON lsc.idobjeto = CAST(s.idstock AS varchar)")
        q.setWhere("tiposincro = 'Enviar stocks' AND NOT sincronizado GROUP BY s.referencia, s.talla, s.disponible, lsc.idobjeto LIMIT 1")

        q.exec_()

        if not q.size():
            return body

        body = self.fetch_query(q)
        self.idlinea = body[0]["lsc.idobjeto"]
        if body[0]["s.talla"] and body[0]["s.talla"] and body[0]["s.talla"] != "TU":
            body[0]["s.referencia"] = body[0]["s.referencia"] + body[0]["s.talla"]
        
        self.referencia = body[0]["s.referencia"]

        if body[0]["s.disponible"] > 0:
            body[0]["status"] = 1
        else:
            body[0]["s.disponible"] = 0
            body[0]["status"] = 0

        return body

    def get_inventory_serializer(self):
        return InventorySerializer()

    def send_data(self, data):
        inventory_url = self.inventory_url if self.driver.in_production else self.inventory_test_url
        
        if data:
            result = self.send_request("post", url=inventory_url, data=json.dumps(data))

        return data

    def after_sync(self, response_data=None):
        print("after_sync")

        qsatype.FLSqlQuery().execSql("UPDATE lineassincro_catalogo SET sincronizado = TRUE WHERE idobjeto = CAST({} as VARCHAR)".format(self.idlinea))

        self.log("Éxito", "Stock sincronizado correctamente (referencia: {})".format(self.referencia))

        return self.small_sleep
