import json
import requests
import time

from AQNEXT.celery import app

from YBUTILS import globalValues

from models.flsyncppal import flsyncppal_def as syncppal


class TaskManager():

    sync_object_dict = None

    def __init__(self, sync_object_dict={}):
        self.sync_object_dict = sync_object_dict

        globalValues.registrarmodulos()
        self.register_tasks()

    def register_tasks(self):
        for sync_object_name in self.sync_object_dict:
            @app.task(name=sync_object_name)
            def decorated(*args):
                self.continuous_task(*args)

    def sync_object_factory(self, sync_object_name):
        if sync_object_name not in self.sync_object_dict:
            return None

        sync_object_dict = self.sync_object_dict[sync_object_name]
        sync_driver = sync_object_dict["driver"] if "driver" in sync_object_dict else None
        return sync_object_dict["sync_object"], sync_driver

    def task_executer(self, sync_object_name, params={}, countdown=0, first=True):
        if "continuous" not in params or not params["continuous"]:
            response = self.sync_task(sync_object_name, params)
            self.log(response["data"]["log"], params)
            return response

        params["url_diagnosis"] = self.get_diagnosis_url(params)
        params["first"] = first
        app.tasks[sync_object_name].apply_async((sync_object_name, params,), countdown=countdown)

        return {"status": 200, "data": {"msg": "Tarea encolada correctamente"}, "countdown": countdown}

    def get_sync_object(self, sync_object_name, params={}):
        sync_object_class, sync_driver = self.sync_object_factory(sync_object_name)

        if sync_driver:
            return sync_object_class(sync_driver(), params)

        return sync_object_class(params)

    def sync_task(self, sync_object_name, params={}, sync_object=None):
        if not sync_object:
            sync_object = self.get_sync_object(sync_object_name, params)

        return sync_object.start()

    def continuous_task(self, sync_object_name, params={}):
        sync_object = self.get_sync_object(sync_object_name, params)
        response = self.sync_task(sync_object_name, params, sync_object=sync_object)

        first = params["first"] if "first" in params else False

        if first:
            params["first"] = False
            time.sleep(3)

        activo = self.get_activo(sync_object.process_name, params)
        if activo:
            self.task_executer(sync_object_name, params=params, countdown=response["countdown"], first=False)
        else:
            response["data"]["log"].append({
                "msg_type": "Info",
                "msg": "Proceso detenido",
                "process_name": sync_object.process_name,
                "customer_name": syncppal.iface.get_customer()
            })

        self.log(response["data"]["log"], params)

    def get_diagnosis_url(self, params={}):
        if "url_diagnosis" in params and params["url_diagnosis"]:
            return params["url_diagnosis"]

        if "production" in params and params["production"]:
            return "https://diagnosis.yeboyebo.es"

        return "http://127.0.0.1:9000"

    def log(self, logs, params={}, retry=False):
        headers = {"Content-Type": "application/json"}
        logs = {"log": logs}

        url = "{}/api/diagnosis/log/append".format(self.get_diagnosis_url(params))

        try:
            response = requests.post(url, headers=headers, data=json.dumps(logs))
            if response.status_code != 200:
                raise NameError("Error. No se pudo escribir en el log")
        except Exception:
            if retry:
                print("Error. No se pudo escribir en el log")
                return False
            else:
                print("Sin conexión. No se pudo escribir en el log. Probando en 60 segundos")
                time.sleep(60)
                return self.log(logs, params, retry=True)

    def get_activo(self, process_name, params={}, retry=False):
        url = "{}/api/diagnosis/process/isactive/{}".format(self.get_diagnosis_url(params), process_name)

        try:
            response = requests.get(url)
            return response.json()["active"]
        except Exception:
            if retry:
                print("Error. No se pudo recibir el estado del proceso")
                return False
            else:
                print("Sin conexión. No se pudo recibir el estado del proceso. Probando en 60 segundos")
                time.sleep(60)
                return self.get_activo(process_name, params, retry=True)

    def get_activity(self):
        i = app.control.inspect()
        active = i.active()
        scheduled = i.scheduled()
        reserved = i.reserved()

        active_process = {}
        for w in active:
            for t in active[w]:
                active_process[t["id"]] = {}
                active_process[t["id"]]["worker"] = w
                active_process[t["id"]]["id"] = t["id"]
                active_process[t["id"]]["pk"] = t["id"]
                active_process[t["id"]]["name"] = t["name"]
                active_process[t["id"]]["args"] = t["args"]
        scheduled_process = {}
        for w in scheduled:
            for t in scheduled[w]:
                scheduled_process[t["request"]["id"]] = {}
                scheduled_process[t["request"]["id"]]["worker"] = w
                scheduled_process[t["request"]["id"]]["eta"] = t["eta"][:19]
                scheduled_process[t["request"]["id"]]["id"] = t["request"]["id"]
                scheduled_process[t["request"]["id"]]["pk"] = t["request"]["id"]
                scheduled_process[t["request"]["id"]]["name"] = t["request"]["name"]
                scheduled_process[t["request"]["id"]]["args"] = t["request"]["args"]
        reserved_process = {}
        for w in reserved:
            for t in reserved[w]:
                reserved_process[t["id"]] = {}
                reserved_process[t["id"]]["worker"] = w
                reserved_process[t["id"]]["id"] = t["id"]
                reserved_process[t["id"]]["pk"] = t["id"]
                reserved_process[t["id"]]["name"] = t["name"]
                reserved_process[t["id"]]["args"] = t["args"]

        return {"active": active_process, "scheduled": scheduled_process, "reserved": reserved_process}

    def revoke(self, id):
        app.control.revoke(id, terminate=True)
        return True
