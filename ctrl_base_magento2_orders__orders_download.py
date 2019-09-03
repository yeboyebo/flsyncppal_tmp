from YBLEGACY import qsatype
from abc import ABC

from controllers.base.magento2.drivers.magento2 import Magento2Driver
from controllers.base.default.controllers.download_sync import DownloadSync
from controllers.base.magento2.orders.serializers.order_serializer import OrderSerializer

from models.flfact_tpv.objects.ordersb2b_raw import OrdersB2B


class OrdersDownload(DownloadSync, ABC):

    orders_url = "<host>/rest/V1/unsynchronized/orders/"
    orders_test_url = "<testhost>/rest/V1/unsynchronized/orders/"

    def __init__(self, process_name, params=None):
        super().__init__(process_name, Magento2Driver(), params)

    def process_data(self, data):
        order_data = OrderSerializer().serialize(data)
        if not order_data:
            self.error_data.append(data)
            return False

        order = OrdersB2B(order_data)
        order.save()

        return True

    def get_data(self):
        orders_url = self.orders_url if self.driver.in_production else self. orders_test_url
        return self.send_request("get", url=orders_url)

    def process_all_data(self, all_data):
        if all_data == []:
            self.log("Éxito", "No hay datos que sincronizar")
            return False

        for data in all_data:
            try:
                if self.process_data(data):
                    self.success_data.append(data)
            except Exception as e:
                self.sync_error(data, e)

        return True

    def after_sync(self):
        self.set_sync_params({
            "url": "http://b2b.elganso.com/index.php/rest/default/V1/orders/{}/synchronized",
            "test_url": "http://magento2.local/index.php/rest/default/V1/orders/{}/synchronized"
        })

        success_records = []
        error_records = []

        for order in self.error_data:
            error_records.append(order["increment_id"])

        after_sync_error_records = []

        for order in self.success_data:
            try:
                self.send_request("post", replace=[order["increment_id"]])
                success_records.append(order["increment_id"])
            except Exception as e:
                self.after_sync_error(order, e)
                after_sync_error_records.append(order["increment_id"])

        if success_records:
            self.log("Éxito", "Los siguientes pedidos B2B se han sincronizado correctamente: {}".format(success_records))

        if error_records:
            self.log("Error", "Los siguientes pedidos B2B no se han sincronizado correctamente: {}".format(error_records))

        if after_sync_error_records:
            self.log("Error", "Los siguientes pedidos  B2B no se han marcado como sincronizados: {}".format(after_sync_error_records))

        return self.small_sleep
