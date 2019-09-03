from abc import ABC
from YBLEGACY import qsatype

from controllers.base.mirakl.orders.controllers.orders_download import OrdersDownload
from controllers.base.mirakl.orders.serializers.ew_ventaseciweb_serializer import VentaseciwebSerializer
from controllers.base.mirakl.orders.serializers.order_serializer import OrderSerializer

from models.flfact_tpv.objects.ew_ventaseciweb_raw import EwVentaseciweb
from models.flfact_tpv.objects.egorder_raw import EgOrder


class ShippingOrdersDownload(OrdersDownload, ABC):

    shipping_url = "<host>/api/orders?order_state_codes=SHIPPING&order_ids={}"
    shipping_test_url = "<host>/api/orders?order_state_codes=SHIPPING&order_ids={}"

    esquema = "SHIPPING_ECI_WEB"
    codtienda = "AEVV"

    def __init__(self, process_name, params=None):
        super().__init__(process_name, params)

    def get_order_serializer(self):
        return OrderSerializer()

    def get_vtaeci_serializer(self):
        return VentaseciwebSerializer()

    def get_order_model(self, data):
        return EgOrder(data)

    def get_vtaeci_model(self, data):
        return EwVentaseciweb(data)

    def get_data(self):
        shipping_url = self.shipping_url if self.driver.in_production else self.shipping_test_url

        order_ids = self.get_order_ids()

        if not order_ids or order_ids == "NOIDS":
            return {"orders": [], "total_count": 0}

        result = self.send_request("get", url=shipping_url.format(",".join(order_ids)))
        return result

    def process_data(self, data):
        if not data:
            self.error_data.append(data)
            return False

        fecha = data["last_updated_date"]
        if self.fecha_sincro != "":
            if fecha > self.fecha_sincro:
                self.fecha_sincro = fecha
        else:
            self.fecha_sincro = fecha

        eciweb_data = self.get_vtaeci_serializer().serialize(data)
        if not eciweb_data:
            return

        order_data = self.get_order_serializer().serialize(data)
        if not order_data:
            return

        order = self.get_order_model(order_data)
        order.save()

        eciweb_data["idtpv_comanda"] = order.cursor.valueBuffer("idtpv_comanda")

        eciweb = self.get_vtaeci_model(eciweb_data)
        eciweb.save()

        return True

    def get_order_ids(self):
        order_ids = []

        q = qsatype.FLSqlQuery()
        q.setSelect("idweb")
        q.setFrom("ew_ventaseciweb")
        q.setWhere("estado = 'WAITING_DEBIT'")

        q.exec_()

        while q.next():
            order_ids.append(q.value(0))

        if order_ids == []:
            return "NOIDS"

        return order_ids
