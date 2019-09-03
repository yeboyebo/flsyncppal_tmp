import requests

from abc import ABC

from controllers.base.default.drivers.default_driver import DefaultDriver


class WebDriver(DefaultDriver, ABC):

    session = None

    success_code = None
    url = None
    test_url = None
    auth = None
    test_auth = None

    def __init__(self):
        self.success_code = 200
        self.session = requests.Session()

    def send_request(self, request_type, url=None, data=None, replace=[], success_code=None, file=None):
        url = url if url else self.get_url(replace)
        headers = self.get_headers()

        response = None

        if file:
            del headers["Content-Type"]
            response = self.session.post(url, headers=headers, data=data, files={"file": open(file, "rb")})
        elif request_type == "get":
            response = self.session.get(url, headers=headers, data=data)
        elif request_type == "post":
            response = self.session.post(url, headers=headers, data=data)
        elif request_type == "put":
            response = self.session.put(url, headers=headers, data=data)
        elif request_type == "delete":
            response = self.session.delete(url, headers=headers, data=data)
        else:
            raise NameError("No se encuentra el tipo de petición {}".format(request_type))

        if not success_code:
            success_code = self.success_code

        return self.proccess_response(response, success_code)

    def get_url(self, replace=[]):
        url = self.url if self.in_production else self.test_url

        if replace:
            url = url.format(*replace)

        if not url or url == "":
            raise NameError("La url no se indicó o no se hizo correctamente")

        return url

    def proccess_response(self, response, success_code):
        if response.status_code == success_code:
            try:
                return response.json()
            except Exception as e:
                raise NameError("Mala respuesta del servidor. {}".format(e))
        else:
            error_text = ""
            if "reason" in response and response["reason"] != "":
                error_text = response.reason
            else:
                error_text = response.text

            raise NameError("Código {}. {}".format(response.status_code, error_text))

    def get_headers(self):
        headers = {
            "Content-Type": "application/json"
        }

        auth = self.auth if self.in_production else self.test_auth
        if auth:
            headers.update({"Authorization": auth})

        return headers
