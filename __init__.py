from flask import flash, Flask, redirect, render_template, request, url_for
from www.editor import editor

from flaskext.login import (LoginManager, current_user, login_required,
                            login_user, logout_user, UserMixin, AnonymousUser,
                            confirm_login, fresh_login_required)

class User(UserMixin):
    def __init__(self, name, id, active=True):
        self.name = name
        self.id = id
        self.active = active

    def is_active(self):
        return self.active


class Anonymous(AnonymousUser):
    name = u"Anonymous"


USERS = {
    1: User(u"rascal", 1),
}

USER_NAMES = dict((u.name, u) for u in USERS.itervalues())

SECRET_KEY = "rascal"
DEBUG = True

app = Flask(__name__)

app.config.from_object(__name__)

login_manager = LoginManager()

login_manager.anonymous_user = Anonymous
login_manager.login_view = "/editor/auth"
login_manager.login_message = u"Please log in to access this page."
login_manager.refresh_view = "/editor/reauth"

@login_manager.user_loader
def load_user(id):
    return USERS.get(int(id))

login_manager.setup_app(app)

app.register_blueprint(editor)
