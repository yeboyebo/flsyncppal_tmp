import psycopg2

from YBLEGACY import qsatype

from controllers.base.default.drivers.sql_driver import SqlDriver


class PsqlStoreDriver(SqlDriver):

    def get_connection_data(self):
        query = qsatype.FLSqlQuery("")
        query.setSelect("usuario, nombrebd, contrasena, puerto, servidor")
        query.setFrom("tpv_tiendas")
        query.setWhere("codtienda = '{}'".format(self.name.upper()))

        if not query.exec_():
            return False

        if not query.first():
            return False

        return "user='{}' password='{}' dbname='{}' host='{}' port='{}'".format(query.value("usuario"), query.value("contrasena"), query.value("nombrebd"), query.value("servidor"), query.value("puerto"))

    def connect(self, connection_data):
        self.connection = psycopg2.connect(connection_data)
        self.cursor = self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    def raw_execute(self, sql):
        self.cursor.execute(sql)

    def fetchall(self):
        return self.cursor.fetchall()

    def commit(self):
        return self.connection.commit()

    def disconnect(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
