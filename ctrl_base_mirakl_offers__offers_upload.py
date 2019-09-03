from abc import ABC
import os
from YBLEGACY import qsatype

from controllers.base.default.controllers.upload_sync import UploadSync
from controllers.base.mirakl.drivers.mirakl import MiraklDriver


class OffersUpload(UploadSync, ABC):

    _ssw = None
    file_name = None

    offers_url = "<host>/api/offers/imports"
    offers_test_url = "<testhost>/api/offers/imports"

    def __init__(self, process_name, params=None):
        super().__init__(process_name, MiraklDriver(), params)

        self.file_name = "offers_{}T{}.csv".format(self.start_date, self.start_time)

    def get_data(self):
        data = self.get_db_data()
        if data == []:
            return data

        with open(self.file_name, "w") as csvfile:
            csvfile.write("\"sku\";\"quantity\"\n")
            for reg in data:
                csvfile.write("{};{}\n".format(reg[0], reg[1]))

        file = open(self.file_name, "r")

        return file

    def get_db_data(self):
        body = []

        disponible_restar = self.get_disponible_a_restar()

        q = qsatype.FLSqlQuery()
        q.setSelect("sw.idssw, s.barcode, s.disponible")
        q.setFrom("eg_sincrostockweb sw INNER JOIN stocks s ON sw.idstock = s.idstock")
        q.setWhere("NOT sincronizadoeci")

        q.exec_()

        if not q.size():
            return body

        while q.next():
            if not self._ssw:
                self._ssw = ""
            else:
                self._ssw += ","
            self._ssw += str(q.value("sw.idssw"))

            disponible = int(q.value("s.disponible")) - int(disponible_restar)
            if disponible < 0:
                disponible = 0

            body.append([q.value("s.barcode"), disponible])

        return body

    def send_data(self, data):
        data = {"import_mode": "PARTIAL_UPDATE"}
        resul = self.send_request("post", url=self.offers_url, data=data, file=self.file_name, success_code=201)
        os.remove(self.file_name)

        return resul

    def get_disponible_a_restar(self):
        cant = qsatype.FLUtil.sqlSelect("param_parametros", "valor", "nombre = 'SEGURIDAD_STOCK'")
        if not cant or cant == None or str(cant) == "None":
            cant = 0
        return cant

    def after_sync(self, response_data=None):
        if response_data and "import_id" in response_data:
            qsatype.FLSqlQuery().execSql("UPDATE eg_sincrostockweb SET sincronizadoeci = TRUE WHERE idssw IN ({})".format(self._ssw))

            self.log("Éxito", "Stock sincronizado correctamente: {}".format(response_data["import_id"]))
        else:
            self.log("Error", "No hubo una respuesta correcta del servidor")

        return self.small_sleep
