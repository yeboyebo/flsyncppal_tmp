from abc import ABC
from YBLEGACY import qsatype
import json
import xmltodict

from datetime import datetime, timedelta

from controllers.base.default.controllers.download_sync import DownloadSync
from controllers.base.mirakl.drivers.mirakl import MiraklDriver
from controllers.base.mirakl.returns.serializers.ew_devolucioneseciweb_serializer import DevolucioneseciwebSerializer
from models.flfact_tpv.objects.ew_devolucioneseciweb_raw import EwDevolucioneseciweb

class ReturnsDownload(DownloadSync, ABC):

    returns_url = "<host>/api/messages?start_date={}"
    returns_test_url = "<testhost>/api/messages?start_date={}"

    fecha_sincro = ""
    esquema = "DEVOLS_ECI_WEB"
    codtienda = "AEVV"

    def __init__(self, process_name, params=None):
        super().__init__(process_name, MiraklDriver(), params)

        self.origin_field = "order_id"

    def process_data(self, data):
        if not data:
            self.error_data.append(data)
            return False

        data["valdemoro"] = False
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

    def masAccionesProcessData(self, eciweb_data):
        return True

    def get_data(self):
        returns_url = self.returns_url if self.driver.in_production else self.returns_test_url

        fecha = self.dame_fechasincrotienda(self.esquema, self.codtienda)
        if fecha and fecha != "None" and fecha != "":
            self.fecha_sincro = fecha
        else:
            self.fecha_sincro = "2000-01-01T00:00:01Z"

        # Tmp. Para pruebas. Quitar en producción
        #self.fecha_sincro = "2000-01-01T00:00:01Z"
        result = self.send_request("get", url=returns_url.format(self.fecha_sincro))
        return result

    def process_all_data(self, all_data):
        if all_data["messages"] == []:
            self.log("Éxito", "No hay datos que sincronizar")
            return False

        processData = False
        for data in all_data["messages"]:
            try:
                datosDevol = json.loads(json.dumps(xmltodict.parse(data["body"])))
                tipoMsg = datosDevol["Mensaje"]["tipoMensaje"]

                fecha = data["date_created"]
                if self.fecha_sincro != "":
                    if fecha > self.fecha_sincro:
                        self.fecha_sincro = fecha
                else:
                    self.fecha_sincro = fecha

                if data["subject"] != "Devolución artículo":
                    continue

                if tipoMsg != "001":
                    continue

                dirRecogida = datosDevol["Mensaje"]["Recogida"]["direccionRecogida"]
                # if dirRecogida.find("VALDEMORO") != -1:
                if dirRecogida == "CTRA/ANDALUCIA KM 23,5S/N,(ATT.DVD). CP: 28343. VALDEMORO":
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

    def after_sync(self):
        if not self.guarda_fechasincrotienda(self.esquema, self.codtienda):
            self.log("Error", "Falló al guardar fecha última sincro")
            return self.small_sleep

        if self.success_data:
            self.log("Éxito", "Las siguientes devoluciones se han sincronizado correctamente: {}".format([order["order_id"] for order in self.success_data]))

        return self.large_sleep

    def guarda_fechasincrotienda(self, esquema, codtienda):
        fecha = str(self.fecha_sincro)[:10]

        fechaSeg = datetime.strptime(self.fecha_sincro, '%Y-%m-%dT%H:%M:%SZ')
        fecha1Seg = fechaSeg + timedelta(seconds=1)
        hora = str(fecha1Seg)[11:19]

        idsincro = qsatype.FLUtil.sqlSelect("tpv_fechasincrotienda", "id", "esquema = '{}' AND codtienda = '{}'".format(esquema, codtienda))

        if idsincro:
            qsatype.FLSqlQuery().execSql("UPDATE tpv_fechasincrotienda SET fechasincro = '{}', horasincro = '{}' WHERE id = {}".format(fecha, hora, idsincro))
        else:
            qsatype.FLSqlQuery().execSql("INSERT INTO tpv_fechasincrotienda (codtienda, esquema, fechasincro, horasincro) VALUES ('{}', '{}', '{}', '{}')".format(codtienda, esquema, fecha, hora))

        return True

    def dame_fechasincrotienda(self, esquema, codtienda):
        return qsatype.FLUtil.sqlSelect("tpv_fechasincrotienda", "fechasincro || 'T' || horasincro || 'Z'", "esquema = '{}' AND codtienda = '{}'".format(esquema, codtienda))

