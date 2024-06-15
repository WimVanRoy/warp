from asgiref.wsgi import WsgiToAsgi
from warp.config import *
from flask import Flask

app = Flask(__name__)

initConfig(app)

from warp import db
db.init(app)

from warp import view
app.register_blueprint(view.bp)

from warp import xhr
app.register_blueprint(xhr.bp, url_prefix='/xhr')

from warp import auth
from warp import auth_mellon
from warp import auth_ldap
if 'AUTH_MELLON' in app.config \
   and 'MELLON_ENDPOINT' in app.config \
   and app.config['AUTH_MELLON']:
    app.register_blueprint(auth_mellon.bp)
elif 'AUTH_LDAP' in app.config \
   and app.config['AUTH_LDAP']:
    app.register_blueprint(auth_ldap.bp)
else:
    app.register_blueprint(auth.bp)

asgi_app = WsgiToAsgi(app)
