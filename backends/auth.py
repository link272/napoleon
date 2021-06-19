from napoleon.core.network.http import HTTPInterface, HTTPClient
from napoleon.properties import Instance, PlaceHolder, DateTime, List, Integer
import datetime
from napoleon.tools.singleton import Nothing


class TokenAuthClient(HTTPClient):

    token_expiration_delta: float = DateTime()
    auth_interface: HTTPInterface = Instance(HTTPInterface)
    _token_expiration_time = PlaceHolder()
    refresh_status_code = List(Integer(), default=[401])

    def _refresh_token(self, query_name="get_token"):
        with self.auth_interface:
            response = self.auth_interface.send(query_name)
        self._token_expiration_time = datetime.datetime.now() + datetime.timedelta(minutes=self.token_expiration_delta)
        self._session.headers.update("Authorization", response.get("token"))

    def build_session(self):
        super().build_session()
        self._refresh_token()

    def send(self, query, data=None, files=None, json=None):
        if self._token_expiration_time < datetime.datetime.now():
            self._refresh_token(query_name="refresh_token")
        return super().send(query=query, data=data, files=files, json=json)

    def handle_error(self, response):
        if response.status_code in self.refresh_status_code:
            self._refresh_token(query_name="refresh_token")
        else:
            super().handle_error(response)

    def __exit__(self, exc_type, exc_val, exc_tb):
        super().__exit__(exc_type, exc_val, exc_tb)
        self._token_expiration_time = Nothing
