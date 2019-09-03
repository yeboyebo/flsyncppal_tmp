# @class_declaration interna #
from YBLEGACY import qsatype


class interna(qsatype.objetoBase):

    ctx = qsatype.Object()

    def __init__(self, context=None):
        self.ctx = context


# @class_declaration flsyncppal #
import requests
import json


class flsyncppal(interna):

    def flsyncppal_get_customer(self):
        return "flsyncppal"

    def flsyncppal_log(self, text, process):
        headers = {"Content-Type": "application/json"}
        a_text = text.split(". ")
        logs = {"log": [{
            "msg_type": a_text[0] if len(a_text) else "Error",
            "msg": ". ".join(a_text[1:]) if len(a_text) else "Log incorrecto",
            "process_name": process,
            "customer_name": self.get_customer()
        }]}

        url = "{}/api/diagnosis/log/append".format(self.get_diagnosis_url())

        try:
            response = requests.post(url, headers=headers, data=json.dumps(logs))
            if response.status_code != 200:
                raise NameError("Error. No se pudo escribir en el log")
        except Exception:
            print("Error. No se pudo escribir en el log")
            return False

    def get_diagnosis_url(self):
        return "https://diagnosis.yeboyebo.es" if qsatype.FLUtil.isInProd() else "http://127.0.0.1:9000"

    def flsyncppal_replace(self, string):
        if string is None or not string or string == "":
            return string
        string = string.replace("'", " ")
        string = string.replace("º", " ")
        string = string.replace("/", " ")
        string = string.replace("\\", " ")
        string = string.replace("\"", " ")
        string = string.replace("\n", " ")
        string = string.replace("\r", " ")
        string = string.replace("\t", " ")
        return string[:255]

    def __init__(self, context=None):
        super().__init__(context)

    def get_customer(self):
        return self.ctx.flsyncppal_get_customer()

    def log(self, text, process):
        return self.ctx.flsyncppal_log(text, process)

    def replace(self, string):
        return self.ctx.flsyncppal_replace(string)


# @class_declaration head #
class head(flsyncppal):

    def __init__(self, context=None):
        super().__init__(context)


# @class_declaration ifaceCtx #
class ifaceCtx(head):

    def __init__(self, context=None):
        super().__init__(context)


# @class_declaration FormInternalObj #
class FormInternalObj(qsatype.FormDBWidget):
    def _class_init(self):
        self.iface = ifaceCtx(self)


form = FormInternalObj()
form._class_init()
form.iface.ctx = form.iface
form.iface.iface = form.iface
iface = form.iface
