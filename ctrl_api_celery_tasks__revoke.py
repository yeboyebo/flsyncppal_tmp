import json

from django.http import HttpResponse

from sync.tasks import task_manager


# @class_declaration interna_revoke #
class interna_revoke():
    pass


# @class_declaration flsyncppal_revoke #
class flsyncppal_revoke(interna_revoke):

    @staticmethod
    def start(pk, data):
        result = task_manager.revoke(pk)

        data = {"result": result}

        return HttpResponse(json.dumps(data), content_type="application/json")


# @class_declaration revoke #
class revoke(flsyncppal_revoke):
    pass
