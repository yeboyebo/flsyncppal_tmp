import json
from abc import ABC, abstractmethod

from controllers.base.default.controllers.connect_sync import ConnectSync


class UploadSync(ConnectSync, ABC):

    def __init__(self, process_name, driver, params=None):
        super().__init__(process_name, driver, params)

    def sync(self):
        data = self.get_data()

        if data == []:
            self.log("Éxito", "No hay datos que sincronizar")
            return self.large_sleep

        response_data = self.send_data(data)
        return self.after_sync(response_data)

    @abstractmethod
    def get_data(self):
        pass

    def send_data(self, data):
        return self.send_request("post", data=json.dumps(data))

    @abstractmethod
    def after_sync(self, response_data=None):
        pass

    def fetch_query(self, q):
        field_list = [field.strip() for field in q.select().split(",")]

        rows = []
        while q.next():
            row = {field: q.value(field) for (field) in field_list}
            rows.append(row)

        return rows
