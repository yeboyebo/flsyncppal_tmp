from abc import ABC, abstractmethod

from controllers.base.default.controllers.default_sync import DefaultSync


class RecieveSync(DefaultSync, ABC):

    def sync_flow(self):
        try:
            return self.sync()
        except Exception as e:
            self.log("Error", e)
            return {"data": {"log": self.logs}, "status": 500}

    @abstractmethod
    def sync(self):
        pass
