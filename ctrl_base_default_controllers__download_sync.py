import requests
import json

from abc import ABC, abstractmethod

from controllers.base.default.controllers.connect_sync import ConnectSync

from models.flsyncppal import flsyncppal_def as syncppal


class DownloadSync(ConnectSync, ABC):

    success_data = None
    error_data = None

    def __init__(self, process_name, driver, params=None):
        super().__init__(process_name, driver, params)

        self.success_data = []
        self.error_data = []

        self.origin_field = "entity_id"

    def sync(self):
        response_data = self.get_data()

        if not self.process_all_data(response_data):
            return self.large_sleep

        return self.after_sync()

    def get_data(self):
        return self.send_request("get")

    def process_all_data(self, all_data):
        if all_data == []:
            self.log("Éxito", "No hay datos que sincronizar")
            return False

        for data in all_data:
            try:
                self.process_data(data)
                self.success_data.append(data)
            except Exception as e:
                self.sync_error(data, e)

        return True

    @abstractmethod
    def process_data(self, data):
        pass

    @abstractmethod
    def after_sync(self, response_data=None):
        pass

    def sync_error(self, data, exc):
        self.error_data.append(data)

        self.log("Error", "Ocurrió un error al sincronizar el registro {}. {}".format(data[self.origin_field], exc))

        if self.params["continuous"]:
            self.add_failed_process(data, exc)

    def after_sync_error(self, data, exc):
        self.log("Error", "Ocurrió un error al marcar como sincronizado el registro {}. {}".format(data[self.origin_field], exc))

    def add_failed_process(self, data, exc):
        headers = {"Content-Type": "application/json"}
        data = {
            "customer_name": syncppal.iface.get_customer(),
            "process_name": self.process_name,
            "error": self.format_string(exc, max_characters=None),
            "pk": data[self.origin_field]
        }

        url = "{}/api/diagnosis/process/failed".format(self.params["url_diagnosis"])

        try:
            response = requests.post(url, headers=headers, data=json.dumps(data))
            if response.status_code != 200:
                raise NameError("Error. No se pudo incluir el registro {} en procesos erróneos. Código {}".format(data["pk"], response.status_code))
        except Exception as e:
            self.log("Error", "No se pudo incluir el registro {} en procesos erróneos. {}".format(data["pk"], e))
            return False
