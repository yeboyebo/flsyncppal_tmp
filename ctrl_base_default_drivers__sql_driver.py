from abc import ABC, abstractmethod

from controllers.base.default.drivers.default_driver import DefaultDriver


class SqlDriver(DefaultDriver, ABC):

    name = None

    connection = None
    cursor = None

    def login(self):
        try:
            connection_data = self.get_connection_data()
            self.connect(connection_data)
            self.execute("SELECT id FROM empresa WHERE 1 = 1")
        except Exception as e:
            raise NameError("No se pudo conectar a la BD {}. {}".format(self.name, e))

    def execute(self, sql):
        try:
            self.raw_execute(sql)

            if sql[:6].upper() != "SELECT":
                return True

            return self.fetchall()
        except Exception as e:
            raise NameError("Falló la query {}. {}".format(sql, e))

    def logout(self):
        self.disconnect()

    @abstractmethod
    def get_connection_data(self):
        pass

    @abstractmethod
    def connect(self, connection_data):
        pass

    @abstractmethod
    def raw_execute(self, sql):
        pass

    @abstractmethod
    def fetchall(self):
        pass

    @abstractmethod
    def commit(self):
        pass

    @abstractmethod
    def disconnect(self):
        pass
