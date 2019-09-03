import requests
import json
from abc import ABC

from YBLEGACY import qsatype

from controllers.base.magento2.drivers.magento2 import Magento2Driver
from controllers.base.default.controllers.upload_sync import UploadSync

from controllers.base.magento2.price.serializers.price_serializer import PriceSerializer


class PriceUpload(UploadSync, ABC):

    price_url = "<host>/rest/default/V1/products"
    price_test_url = "<testhost>/rest/default/V1/products"

    idlinea = None
    idsincro = None
    referencia = None

    def __init__(self, process_name, params=None):
        super().__init__(process_name, Magento2Driver(), params)

    def get_data(self):
        data = self.get_db_data()

        if data == []:
            return data

        price = self.get_price_serializer().serialize(data[0])

        if not price:
            return False

        return {
            "product": price
        }

    def get_db_data(self):
        body = []

        idlinea = qsatype.FLUtil.sqlSelect("lineassincro_catalogo", "id", "tiposincro = 'Enviar precio producto' AND NOT sincronizado ORDER BY id LIMIT 1")

        if not idlinea:
            return body

        self.idlinea = idlinea

        q = qsatype.FLSqlQuery()
        q.setSelect("lsc.id, lsc.idsincro, lsc.idobjeto, a.pvp, lsc.descripcion")
        q.setFrom("lineassincro_catalogo lsc INNER JOIN articulostarifas a ON lsc.idobjeto = CAST(a.id as varchar) INNER JOIN tarifas t ON a.codtarifa = t.codtarifa")
        q.setWhere("lsc.id = {} GROUP BY lsc.id, lsc.idsincro, lsc.idobjeto, a.pvp, lsc.descripcion".format(self.idlinea))

        q.exec_()

        if not q.size():
            return body

        body = self.fetch_query(q)
        self.idsincro = body[0]["lsc.idsincro"]
        self.id = body[0]["lsc.idobjeto"]
        self.referencia = body[0]["lsc.descripcion"]
        self.error = False

        return body

    def get_price_serializer(self):
        return PriceSerializer()

    def send_data(self, data):
        price_url = self.price_url if self.driver.in_production else self.price_test_url

        del data["product"]["children"]
        if data:
            result = True
            try:
                result = self.send_request("post", url=price_url, data=json.dumps(data))
                print("Result")
                print(result)
            except Exception as e:
                print("exception")
                # print(json.dumps(e))
                self.error = True
                error = "Hubo un error al guardar el precio para la línea " + str(self.idlinea) + " - " + str(self.referencia)
                self.sync_error(data, error)

        return data

    def after_sync(self, response_data=None):
        print("after_sync")
        if self.error == True:
            print("saltado")
            return self.small_sleep

        qsatype.FLSqlQuery().execSql("UPDATE lineassincro_catalogo SET sincronizado = TRUE WHERE id = {}".format(self.idlinea))

        lineas_no_sincro = qsatype.FLUtil.sqlSelect("lineassincro_catalogo", "id", "idsincro = '{}' AND NOT sincronizado LIMIT 1".format(self.idsincro))

        if not lineas_no_sincro:
            qsatype.FLSqlQuery().execSql("UPDATE sincro_catalogo SET ptesincro = FALSE WHERE idsincro = '{}'".format(self.idsincro))

        self.log("Éxito", "Precio sincronizado correctamente (referencia: {})".format(self.referencia))

        return self.small_sleep

    def sync_error(self, data, exc):
        print("sync_error")
        self.add_failed_process(data, exc)
        self.after_sync_error(data, exc)

    def after_sync_error(self, data, exc):
        print("after sync error")
        qsatype.FLSqlQuery().execSql("UPDATE lineassincro_catalogo SET sincronizado = TRUE WHERE id = {}".format(self.idlinea))

        print("1")
        # qsatype.FLSqlQuery().execSql("INSERT INTO erroressincro_catalogo (idlineasincro, descripcion) VALUES ({}, '{}')".format(self.idlinea, str(exc)))

        print("2")
        lineas_no_sincro = qsatype.FLUtil.sqlSelect("lineassincro_catalogo", "id", "idsincro = '{}' AND NOT sincronizado LIMIT 1".format(self.idsincro))

        print("3")
        if not lineas_no_sincro:
            qsatype.FLSqlQuery().execSql("UPDATE sincro_catalogo SET ptesincro = FALSE WHERE idsincro = '{}'".format(self.idsincro))

        print("fin")
        self.log("Error", "Referencia no procesada: {})".format(self.referencia))

        return self.small_sleep

    def add_failed_process(self, data, exc):
        print("add_failed_process")

        headers = {"Content-Type": "application/json"}
    
        data = {
        	"customer_name": "elganso",
            "referencia": self.referencia,
            "process_name": "mgb2bprice",
            "error": str(exc),
            "pk": self.idlinea
        }
   
        url = "{}/api/diagnosis/process/failed".format(self.params["url_diagnosis"])
        print(url)
        # print(str(exc))
        try:
            response = requests.post(url, headers=headers, data=json.dumps(data))
            print(response)
            if response.status_code != 200:
                raise NameError("Error. No se pudo incluir el registro {} en procesos erróneos. Código {}".format(data["pk"], response.status_code))
        except Exception as e:
            self.log("Error", "No se pudo incluir el registro {} en procesos erróneos. {}".format(data["pk"], e))
            return False
