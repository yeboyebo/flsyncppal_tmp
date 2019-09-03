import json
from abc import ABC

from YBLEGACY import qsatype

from controllers.base.magento2.drivers.magento2 import Magento2Driver
from controllers.base.default.controllers.upload_sync import UploadSync

from controllers.base.magento2.tierprice.serializers.tierprice_serializer import TierpriceSerializer


class TierpriceUpload(UploadSync, ABC):

    tierprice_url = "<host>/rest/default/V1/products/tier-prices"
    tierprice_test_url = "<testhost>/rest/default/V1/products/tier-prices"

    idlinea = None
    idsincro = None
    referencia = None

    def __init__(self, process_name, params=None):
        super().__init__(process_name, Magento2Driver(), params)

    def get_data(self):
        data = self.get_db_data()

        if data == []:
            return data

        tierprice = self.get_tierprice_serializer().serialize(data[0])

        if not tierprice:
            return tierprice

        return {
            "prices": [tierprice]
        }

    def get_db_data(self):
        body = []

        idlinea = qsatype.FLUtil.sqlSelect("lineassincro_catalogo", "id", "tiposincro = 'Enviar tarifas' AND NOT sincronizado ORDER BY id LIMIT 1")

        if not idlinea:
            return body

        self.idlinea = idlinea

        q = qsatype.FLSqlQuery()
        q.setSelect("lsc.id, lsc.idsincro, lsc.idobjeto, a.pvp, lsc.descripcion, a.codtarifa, gcb2b.grupoclientesb2b")
        q.setFrom("lineassincro_catalogo lsc INNER JOIN articulostarifas a ON lsc.idobjeto = CAST(a.id as varchar) INNER JOIN tarifas t ON a.codtarifa = t.codtarifa INNER JOIN gruposclienteb2b gcb2b ON t.idgrupoclienteb2b = gcb2b.id")
        q.setWhere("lsc.id = {} GROUP BY lsc.id, lsc.idsincro, lsc.idobjeto, a.pvp, lsc.descripcion, a.codtarifa, gcb2b.grupoclientesb2b".format(self.idlinea))

        q.exec_()

        if not q.size():
            return body

        body = self.fetch_query(q)
        self.idsincro = body[0]["lsc.idsincro"]
        self.id = body[0]["lsc.idobjeto"]
        self.referencia = body[0]["a.codtarifa"] + " - " + body[0]["lsc.descripcion"]

        return body

    def get_tierprice_serializer(self):
        return TierpriceSerializer()

    def send_data(self, data):
        tierprice_url = self.tierprice_url if self.driver.in_production else self.tierprice_test_url

        del data["prices"][0]["children"]
        print(data)
        if data:
        	self.send_request("post", url=tierprice_url, data=json.dumps(data))

        return data

    def after_sync(self, response_data=None):
        qsatype.FLSqlQuery().execSql("UPDATE lineassincro_catalogo SET sincronizado = TRUE WHERE id = {}".format(self.idlinea))

        lineas_no_sincro = qsatype.FLUtil.sqlSelect("lineassincro_catalogo", "id", "idsincro = '{}' AND NOT sincronizado LIMIT 1".format(self.idsincro))

        if not lineas_no_sincro:
            qsatype.FLSqlQuery().execSql("UPDATE sincro_catalogo SET ptesincro = FALSE WHERE idsincro = '{}'".format(self.idsincro))

        self.log("Éxito", "Tarifas sincronizadas correctamente (tarifa - referencia: {})".format(self.referencia))

        return self.small_sleep
