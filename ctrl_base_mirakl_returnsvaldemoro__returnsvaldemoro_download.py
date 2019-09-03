from abc import ABC
from YBLEGACY import qsatype
import json
import xmltodict

from datetime import datetime, timedelta

# from controllers.base.default.controllers.download_sync import DownloadSync
from controllers.base.mirakl.drivers.mirakl import MiraklDriver
from controllers.base.mirakl.returns.serializers.ew_devolucioneseciweb_serializer import DevolucioneseciwebSerializer
from controllers.base.mirakl.returns.controllers.returns_download import ReturnsDownload
from models.flfact_tpv.objects.ew_devolucioneseciweb_raw import EwDevolucioneseciweb

class ReturnsValdemoroDownload(ReturnsDownload, ABC):

    esquema = "DEVOLSVAL_ECI_WEB"

    def process_data(self, data):
        if not data:
            self.error_data.append(data)
            return False

        data["valdemoro"] = True
        eciweb_data = DevolucioneseciwebSerializer().serialize(data)
        if not eciweb_data:
            self.error_data.append(data)
            return False

        if qsatype.FLUtil.sqlSelect("ew_devolucioneseciweb", "idventaweb", "idventaweb = '{}'".format(eciweb_data["idventaweb"])):
            self.log("Error", "La venta {} ya ha sido procesada".format(eciweb_data["idventaweb"]))
            return True

        idComanda = self.masAccionesProcessData(eciweb_data)
        if not idComanda:
            raise NameError("No se pudo crear la devolución")

        eciweb_data["idtpv_comanda"] = idComanda
        eciweb_data["datosdevol"] = data["body"]
        devoleciweb = EwDevolucioneseciweb(eciweb_data)
        devoleciweb.save()

        return True

    def process_all_data(self, all_data):
        if all_data["messages"] == []:
            self.log("Éxito", "No hay datos que sincronizar")
            return False

        processData = False
        for data in all_data["messages"]:
            try:
                fecha = data["date_created"]
                if self.fecha_sincro != "":
                    if fecha > self.fecha_sincro:
                        self.fecha_sincro = fecha
                else:
                    self.fecha_sincro = fecha

                if data["subject"] != "Devolución artículo":
                    continue

                datosDevol = json.loads(json.dumps(xmltodict.parse(data["body"])))
                tipoMsg = datosDevol["Mensaje"]["tipoMensaje"]

                if tipoMsg != "001":
                    continue

                dirRecogida = datosDevol["Mensaje"]["Recogida"]["direccionRecogida"]
                # if dirRecogida.find("VALDEMORO") == -1:
                if dirRecogida != "CTRA/ANDALUCIA KM 23,5S/N,(ATT.DVD). CP: 28343. VALDEMORO":
                    continue

                processData = True
                if self.process_data(data):
                    self.success_data.append(data)
            except Exception as e:
                self.sync_error(data, e)

        if processData == False:
            self.log("Éxito", "No hay datos que sincronizar")
            return False

        return True