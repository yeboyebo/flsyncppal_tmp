from abc import ABC


class DefaultSerializer(ABC):

    init_data = None
    data = None

    def serialize(self, init_data):
        self.init_data = init_data
        self.data = {
            "children": {}
        }
        if not self.get_data():
            return False

        return self.data

    def get_init_value(self, init_key):
        value = self.init_data

        init_keys = init_key.split("//")
        for key in init_keys:
            if key not in value.keys():
                return None
            value = value[key]

        return value

    def set_data_value(self, data_key, value):
        new_dict = self.data

        data_keys = data_key.split("//")
        for key in data_keys[:-1]:
            if key not in new_dict:
                new_dict[key] = {}
            new_dict = new_dict[key]

        new_dict[data_keys[-1]] = value

    def set_string_value(self, data_key, value, max_characters=255, skip_replace=False):
        if value is None:
            self.set_data_value(data_key, value)
            return

        self.set_data_value(data_key, self.format_string(value, max_characters=max_characters, skip_replace=skip_replace))

    def set_data_relation(self, data_key, init_key, default=None):
        value = self.get_init_value(init_key)

        if value is None and default is not None:
            value = default

        self.set_data_value(data_key, value)

    def set_string_relation(self, data_key, init_key, max_characters=255, default=None, skip_replace=False):
        value = self.get_init_value(init_key)

        if (value is None or value == "") and default is not None:
            value = default

        self.set_string_value(data_key, value, max_characters=max_characters, skip_replace=skip_replace)

    def format_string(self, string, max_characters=255, skip_replace=False):
        if string is None or not string or string == "":
            return string

        string = str(string)

        if not skip_replace:
            string = string.replace("'", " ")
            string = string.replace("º", " ")
            string = string.replace("/", " ")
            string = string.replace("\\", " ")
            string = string.replace("\"", " ")
            string = string.replace("\n", " ")
            string = string.replace("\r", " ")
            string = string.replace("\t", " ")

        return string[:max_characters]
