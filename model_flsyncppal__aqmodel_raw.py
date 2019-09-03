from YBLEGACY import qsatype

from abc import ABC

from YBUTILS.viewREST import cacheController


class AQModel(ABC):

    table = None
    data = None
    cursor = None
    children = None
    is_insert = None
    params = None
    skip_record = None

    def __init__(self, table, data, params=None):
        self.table = table
        self.data = data
        self.children = []
        self.params = params
        self.skip_record = not data

        if not self.skip_record:
            self.get_children_data()

    def get_cursor(self):
        cursor = qsatype.FLSqlCursor(self.table)
        cursor.setModeAccess(cursor.Insert)
        cursor.refreshBuffer()

        self.is_insert = True

        return cursor

    def dump_to_cursor(self):
        if not self.cursor:
            self.cursor = self.get_cursor()

        for key, value in self.data.items():
            if key == "children":
                continue
            self.cursor.setValueBuffer(key, value)

    def save(self):
        if self.skip_record:
            return

        self.dump_to_cursor()

        pk_name = self.cursor._model._meta.pk.name

        if not self.cursor.commitBuffer():
            error = cacheController.getSessionVariable("ErrorHandler")

            raise NameError("No se pudo guardar el registro {} de la tabla {}. {}".format(self.data[pk_name], self.table, error))

        for child in self.children:
            if child.skip_record:
                continue

            child.get_parent_data(self.cursor)
            child.save()

    def get_children_data(self):
        return

    def get_parent_data(self, cursor):
        return

    def set_data_value(self, data_key, value):
        self.data[data_key] = value

    def set_string_value(self, data_key, value, max_characters=255):
        if value is None:
            self.set_data_value(data_key, value)
            return

        self.set_data_value(data_key, self.format_string(value, max_characters=max_characters))

    def format_string(self, string, max_characters=255):
        if string is None or not string or string == "":
            return string

        string = str(string)
        string = string.replace("'", " ")
        string = string.replace("º", " ")
        string = string.replace("/", " ")
        string = string.replace("\\", " ")
        string = string.replace("\"", " ")
        string = string.replace("\n", " ")
        string = string.replace("\r", " ")
        string = string.replace("\t", " ")

        return string[:max_characters]
