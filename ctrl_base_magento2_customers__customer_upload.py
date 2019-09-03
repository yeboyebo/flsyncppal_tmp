import requests
import json
from abc import ABC

from YBLEGACY import qsatype

from controllers.base.magento2.drivers.magento2 import Magento2Driver
from controllers.base.default.controllers.upload_sync import UploadSync

from controllers.base.magento2.customers.serializers.customer_serializer import CustomerSerializer


class CustomerUpload(UploadSync, ABC):

    customer_url = "<host>/rest/default/V1/customers"
    customer_test_url = "<testhost>/rest/default/V1/customers"

    customer_put_url = "<host>/rest/default/V1/customers/"
    customer_put_test_url = "<testhost>/rest/default/V1/customers/"

    idlinea = None
    codcliente = None
    idclientemagento = None

    def __init__(self, process_name, params=None):
        super().__init__(process_name, Magento2Driver(), params)

    def get_data(self):
        data = self.get_db_data()

        if data == []:
            return data

        customer = self.get_customer_serializer().serialize(data[0])
        if not customer:
            return False

        return customer

    def get_db_data(self):
        body = []
        self.codcliente = False
        idlinea = qsatype.FLUtil.sqlSelect("lineassincro_catalogo", "id", "tiposincro = 'Enviar clientes' AND NOT sincronizado ORDER BY id LIMIT 1")

        if not idlinea:
            return body

        self.idlinea = idlinea

        q = qsatype.FLSqlQuery()
        q.setSelect("lsc.id, lsc.idobjeto, c.nombre, b2b.cifnif, b2b.email, b2b.codtarifa, dc.provincia, dc.codpais, dc.codpostal, dc.ciudad, dc.direccion, c.telefono1, c.cifnif, gcb2b.idgrupoclienteb2b, c.nombrecomercial, md5(c.cifnif), b2b.idstore, b2b.idclientemagento, dc.dirtipovia, dc.dirotros")
        q.setFrom("lineassincro_catalogo lsc INNER JOIN clientesb2b b2b ON lsc.idobjeto = b2b.codcliente INNER JOIN clientes c ON b2b.codcliente = c.codcliente INNER JOIN dirclientes dc ON c.codcliente = dc.codcliente INNER JOIN gruposclientes gc ON c.codgrupo = gc.codgrupo INNER JOIN tarifas tf ON gc.codtarifa = tf.codtarifa INNER JOIN gruposclienteb2b gcb2b ON tf.idgrupoclienteb2b = gcb2b.id")
        q.setWhere("lsc.id = {} AND lsc.sincronizado = false AND b2b.activo AND dc.domenvio GROUP BY lsc.id, lsc.idobjeto, c.nombre, b2b.cifnif, b2b.email, b2b.codtarifa, dc.provincia, dc.codpais, dc.codpostal, dc.ciudad, dc.direccion, c.telefono1, c.cifnif, gcb2b.idgrupoclienteb2b, c.nombrecomercial, b2b.idstore, b2b.idclientemagento, dc.dirtipovia, dc.dirotros".format(self.idlinea))

        q.exec_()

        if not q.size():
            return body

        body = self.fetch_query(q)
        self.codcliente = body[0]["lsc.idobjeto"]
        self.error = False

        return body

    def get_customer_serializer(self):
        return CustomerSerializer()

    def send_data(self, data):
        customer_url = self.customer_url if self.driver.in_production else self.customer_test_url

        if "children" in data:
            del data["children"]

        print("Data: ", data)
        if data:
            try:
                if "id" in data["customer"]:
                    customer_put_url = self.customer_put_url if self.driver.in_production else self.customer_put_test_url
                    customer_put_url = str(customer_put_url) + str(data["customer"]["id"])
                    response = self.send_request("put", url=customer_put_url, data=json.dumps(data))
                    if "id" in response:
                        self.idclientemagento = response["id"]
                else:
                    response = self.send_request("post", url=customer_url, data=json.dumps(data))
                    if "id" in response:
                        self.idclientemagento = response["id"]

                if not self.idclientemagento or self.idclientemagento == "" or str(self.idclientemagento) == "None":
                    self.error = True
                    error = "Hubo un error al recoger el Id. Magento del cliente para la línea " + str(self.idlinea) + " - " + str(self.codcliente)
                    self.sync_error(data, error)

            except Exception as e:
                self.error = True
                error = "Hubo un error al guardar el cliente para la línea " + str(self.idlinea) + " - " + str(self.codcliente)
                self.sync_error(data, error)

        return data

    def after_sync(self, response_data=None):
        if self.error == True:
            return self.small_sleep

        qsatype.FLSqlQuery().execSql("UPDATE lineassincro_catalogo SET sincronizado = TRUE WHERE id = {}".format(self.idlinea))
        qsatype.FLSqlQuery().execSql("UPDATE clientesb2b SET idclientemagento = '" + str(self.idclientemagento) + "' WHERE codcliente = '" + str(self.codcliente) + "'")

        self.log("Éxito", "Cliente sincronizado correctamente: {}".format(self.codcliente))

        return self.small_sleep

    def sync_error(self, data, exc):
        self.add_failed_process(data, exc)
        self.after_sync_error(data, exc)

    def after_sync_error(self, data, exc):
        qsatype.FLSqlQuery().execSql("UPDATE lineassincro_catalogo SET sincronizado = TRUE WHERE id = {}".format(self.idlinea))
        self.log("Error", "Cliente no procesado: {}".format(self.codcliente))

        return self.small_sleep

    def add_failed_process(self, data, exc):

        headers = {"Content-Type": "application/json"}

        data = {
            "customer_name": "elganso",
            "referencia": self.codcliente,
            "process_name": "mgb2bcustomers",
            "error": str(exc),
            "pk": self.idlinea
        }

        url = "{}/api/diagnosis/process/failed".format(self.params["url_diagnosis"])
        try:
            response = requests.post(url, headers=headers, data=json.dumps(data))
            print(response.text)
            if response.status_code != 200:
                raise NameError("Error. No se pudo incluir el registro {} en procesos erróneos. Código {}".format(data["pk"], response.status_code))
        except Exception as e:
            self.log("Error", "No se pudo incluir el registro {} en procesos erróneos. {}".format(data["pk"], e))
            return False
