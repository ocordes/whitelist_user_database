"""

app/main/routes.py

written by: Oliver Cordes 2021-02-12
changed by: Oliver Cordes 2021-02-12

"""

import os
from datetime import datetime, timedelta
from dateutil.relativedelta import *

from flask import current_app, request, render_template, url_for, flash,  \
                  redirect, send_from_directory, jsonify, session
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse, url_unparse


from app import db
from app.main import bp
from app.models import *



APP_ROOT = os.path.dirname(os.path.abspath(__file__))


"""
before_request will be executed before any page will be
rendered
"""
@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@bp.route('/')
@bp.route('/index')
@login_required
def index():
    return render_template('index.html',
                            title='Dashboard'
                            )


@bp.route('/users')
def show_users():
    return render_template('users.html',
                            title='Whitelist Users')
