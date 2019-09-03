import json

from controllers.base.default.drivers.web_driver import WebDriver


class DrupalDriver(WebDriver):

    session_id = None
    session_name = None
    user_token = None

    login_user = None
    test_login_user = None
    login_password = None
    test_login_password = None

    login_url = None
    test_login_url = None
    logout_url = None
    test_logout_url = None

    def get_headers(self):
        headers = super().get_headers()

        if self.session_id and self.session_name:
            headers.update({"Cookie": "{}={}".format(self.session_name, self.session_id)})

        if self.user_token:
            headers.update({"X-CSRF-Token": self.user_token})

        return headers

    def login(self):
        url = self.login_url if self.in_production else self.test_login_url
        user = self.login_user if self.in_production else self.test_login_user
        password = self.login_password if self.in_production else self.test_login_password

        body = {
            "username": user,
            "password": password
        }

        self.session_id = None
        self.session_name = None
        self.user_token = None

        response = self.send_request("post", url, data=json.dumps(body), success_code=200)
        if response:
            self.session_name = response["session_name"]
            self.session_id = response["sessid"]
            self.user_token = response["token"]

        return True

    def logout(self):
        url = self.logout_url if self.in_production else self.test_logout_url

        self.send_request("post", url, data={}, success_code=200)

        return True
