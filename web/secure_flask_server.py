from pony.orm import Required, Optional
from flask_login import UserMixin
from flask_login import LoginManager
from flask import render_template, request, flash, redirect
from flask_login import logout_user, login_user, login_required
from datetime import datetime
from pony.orm import flush
from napoleon.properties import Integer, String, Alias
import hmac
import os
import hashlib
from napoleon.web.persistent_flask_server import PersistentFlaskServer
from napoleon.core.storage.database import Database, DATABASES


class SecureFlaskServer(PersistentFlaskServer):

    pbkdf2_algorithm: str = String('sha256')
    pbkdf2_iteration: int = Integer(1000000)

    def _hasher(self, password, salt):
        return hashlib.pbkdf2_hmac(self.pbkdf2_algorithm, password.encode(), salt, self.pbkdf2_iteration)

    def build_app(self):
	app = super().build_app()
        return self.build_auth_layer(app)

    def build_auth_layer(self, flask_app):

        if not hasattr(self.database.db, "User"):

            class User(self.database.entity, UserMixin):
                login = Required(str, unique=True)
                hashed_password = Required(bytes)
                salt = Required(bytes)
                last_login = Optional(datetime)

        login_manager = LoginManager(flask_app)
        login_manager.login_view = 'login'

        @login_manager.user_loader
        def load_user(user_id):
            return self.database.db.User.get(id=user_id)

        @flask_app.route('/login', methods=['GET', 'POST'])
        def login():
            if request.method == 'POST':
                username = request.form['username']
                password = request.form['password']
                candidate = self.database.db.User.get(login=username)
                if not candidate:
                    flash('Wrong username')
                    return redirect('/login')
                client_hashed_password = self._hasher(password, candidate.salt)
                if hmac.compare_digest(client_hashed_password, candidate.hashed_password):
                    candidate.last_login = datetime.now()
                    login_user(candidate)
                    return redirect('/')

                flash('Wrong password')
                return redirect('/login')
            else:
                return render_template('login.html')

        @flask_app.route('/register', methods=['GET', 'POST'])
        def register():
            if request.method == 'POST':
                username = request.form['username']
                password = request.form['password']
                exist = self.database.db.User.get(login=username)
                if exist:
                    flash('Username %s is already registered' % username)
                    return redirect('/register')
                salt = os.urandom(16)
                hashed_password = self._hasher(password, salt)
                user = db.User(login=username, hashed_password=hashed_password, salt=salt, last_login=datetime.now()) # noqa
                flush()
                login_user(user)
                flash('Successfully registered')
                return redirect('/')
            else:
                return render_template('register.html')

        @flask_app.route('/logout')
        @login_required
        def logout():
            logout_user()
            flash('Logged out')
            return redirect('/login')

        return flask_app

    def add_view(self, view, route, auth=True):
        _view = login_required(view) if auth else view
        self.app.add_url_rule(route, view_func=_view)
