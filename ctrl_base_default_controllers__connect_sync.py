from abc import ABC, abstractmethod

from controllers.base.default.controllers.default_sync import DefaultSync


class ConnectSync(DefaultSync, ABC):

    small_sleep = None
    large_sleep = None
    no_sync_sleep = None

    def __init__(self, process_name, driver, params=None):
        super().__init__(process_name, params)

        self.driver = driver

        self.small_sleep = 10
        self.large_sleep = 180
        self.no_sync_sleep = 300

    def sync_flow(self):
        try:
            if not self.before_sync():
                self.log("Éxito", "No es momento de sincronizar")
                return {"countdown": self.no_sync_sleep, "data": {"log": self.logs}, "status": 200}

            self.driver.in_production = self.params["production"] if "production" in self.params else False

            self.driver.login()
            sync_result = self.sync()
            self.driver.logout()

            return {"countdown": sync_result, "data": {"log": self.logs}, "status": 200}

        except Exception as e:
            self.log("Error", e)
            return {"countdown": self.large_sleep, "data": {"log": self.logs}, "status": 500}

    def before_sync(self):
        return True

    @abstractmethod
    def sync(self):
        pass

    @abstractmethod
    def after_sync(self, response_data=None):
        pass

    def set_sync_params(self, params):
        for prop in params:
            setattr(self.driver, prop, params[prop])

    def send_request(self, *args, **kwargs):
        return self.driver.send_request(*args, **kwargs)

    def execute(self, *args, **kwargs):
        return self.driver.execute(*args, **kwargs)
