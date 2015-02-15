
# Doc links:
# http://psa.matiasaguirre.net/docs/configuration/flask.html
# http://psa.matiasaguirre.net/docs/backends/facebook.html
# http://flask-login.readthedocs.org/en/latest/
# https://pypi.python.org/pypi/flask-appconfig
# http://pythonhosted.org/Flask-Bootstrap/index.html

import os
import sys
from flask import Flask, render_template, redirect, g, request
from flask_bootstrap import Bootstrap
from flask_appconfig import AppConfig
from social.apps.flask_app.routes import social_auth
from social.apps.flask_app.me.models import init_social, FlaskStorage
from flask.ext import login, mongoengine
from social.apps.flask_app.template_filters import backends
from mrq.job import queue_job
from mrq.context import setup_context
import json

sys.path.append(os.path.abspath(os.path.join(__file__, '../..')))

DEBUG = bool(os.getenv("IMGFAB_DEBUG"))

app = Flask('imgfab')
AppConfig(app, os.path.abspath(os.path.join(__file__, '../settings.py')))
Bootstrap(app)

app.config.update({
  "DEBUG": DEBUG
})

db = mongoengine.MongoEngine(app)
app.register_blueprint(social_auth)
init_social(app, db)
app.context_processor(backends)

login_manager = login.LoginManager()
login_manager.init_app(app)

setup_context()


@app.route("/data/facebook/albums")
@login.login_required
def data_facebook_albums():
    return json.dumps(g.user.get_facebook_albums())


@app.route("/create_task", methods=["POST"])
@login.login_required
def create_task():
    taskpath = request.form['path']
    taskparams = json.loads(request.form['params'])

    if taskpath.startswith("admin"):
        return None

    taskparams["user"] = str(g.user.id)

    job_id = queue_job("tasks.%s" % taskpath, taskparams)

    return str(job_id)


@app.route('/')
def main():
    return render_template('index.html')


@app.route('/logout')
@login.login_required
def logout():
    """Logout view"""
    login.logout_user()
    return redirect('/')


@login_manager.user_loader
def load_user(userid):
    from flaskapp.models import User
    try:
        return User.objects.get(id=userid)
    except Exception, e:
        print "Exception when logging in", e
        pass


@app.before_request
def global_user():
    g.user = login.current_user


# Make current user available on templates
@app.context_processor
def inject_user():
    try:
        return {'user': g.user}
    except AttributeError:
        return {'user': None}

if __name__ == '__main__':
  app.run(debug=DEBUG)
