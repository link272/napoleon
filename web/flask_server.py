from flask import Flask, request
from napoleon.core.special.hidden import HiddenString
import secrets
from napoleon.properties import PlaceHolder, Alias, Boolean
from napoleon.core.paths import PATHS, Path, FilePath
from napoleon.core.network.http import HTTPQuery, HTTPSession
from napoleon.core.network.client import Client, CLIENTS

from napoleon.core.daemon.server import ThreadedServer
from napoleon.tools.singleton import exist

import threading


class FlaskServer(ThreadedServer):

    secret_key = HiddenString(secrets.token_urlsafe)
    _shutdown_token = HiddenString(secrets.token_urlsafe)
    app = PlaceHolder()
    server_client = Alias(Client, CLIENTS)
    debug = Boolean(default=True)
    key_filepath = FilePath(PATHS.docs / Path("crt.pem"))
    crt_filepath = FilePath(PATHS.docs / Path("crt.pem"))
    template_folder = FilePath(PATHS.templates)
    static_folder = FilePath(PATHS.static)

    def _build_internal(self):
        self.app = self.build_app()

    def get_ssl_context(self):
        context = None
        if self.server_client.scheme == "https":
            if exist(self.key_filepath) and exist(self.crt_filepath):
                context = (self.crt_filepath, self.key_filepath)
            else:
                context = "adhoc"
        return context

    def _start_thread(self):
        self._thread = threading.Thread(target=self.app.run,
                                        kwargs={'host': self.server_client.host,
                                                'port': self.server_client.port,
                                                "debug": self.debug,
                                                "use_reloader": False,
                                                "ssl_context": self.get_ssl_context()},  # noqa
                                        daemon=self.daemon)
        self._thread.start()

    def _stop_thread(self):
        shutdown_session = HTTPSession(client=self.server_client)
        with shutdown_session:
            shutdown_session.send(HTTPQuery(root=f"/shutdown/{self._shutdown_token}", method="POST"))

    def build_app(self):
        return self.build_base_app()


    def build_base_app(self):
        flask_app = Flask(__name__,
                          template_folder=str(self.template_folder),
                          static_folder=str(self.static_folder))
        flask_app.secret_key = self.secret_key

        @flask_app.route('/shutdown/<token>', methods=['POST'])
        def shutdown(token):
            if secrets.compare_digest(self._shutdown_token, token):
                request.environ.get('werkzeug.server.shutdown')()
            return "", 204

        return flask_app

    def add_view(self, view, route):
        self.app.add_url_rule(route, view_func=view)
