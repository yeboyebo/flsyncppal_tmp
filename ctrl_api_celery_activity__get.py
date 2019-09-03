import json

from django.http import HttpResponse

from sync.tasks import task_manager


# @class_declaration interna_get #
class interna_get():
    pass


# @class_declaration flsyncppal_get #
class flsyncppal_get(interna_get):

    @staticmethod
    def start(pk, data):
        data = task_manager.get_activity()

        return HttpResponse(json.dumps(data), content_type="application/json")


# @class_declaration get #
class get(flsyncppal_get):
    pass
