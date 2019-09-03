from abc import ABC, abstractmethod


class DefaultDriver(ABC):

    in_production = None

    @abstractmethod
    def login(self):
        pass

    @abstractmethod
    def logout(self):
        pass
