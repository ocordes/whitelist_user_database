"""

app/main/routes.py

written by: Oliver Cordes 2021-02-12
changed by: Oliver Cordes 2021-02-18

"""

import os
from datetime import datetime, timedelta
from dateutil.relativedelta import *

from flask import current_app, request, render_template, url_for, flash,  \
    redirect, send_from_directory, jsonify, session, make_response
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse, url_unparse


from app import db
from app.main import bp
from app.models import *
from app.main.forms import WhitelistGroupForm, DeleteWhitelistGroupForm, \
    AddUserForm, UploadUserForm

from app.auth.admin import admin_required


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


@bp.route('/whiteusers')
def show_users():
    return render_template('users.html',
                            title='Whitelist Users')


@bp.route('/whitelistgroups', methods=['GET','POST'])
@login_required
@admin_required
def whitelistgroups():
    rform = WhitelistGroupForm()
    rform.role.choices = [(r.id, r.name) for r in Roles.query.all()]
    
    dform=DeleteWhitelistGroupForm()
    if dform.validate_on_submit():
        # get a list of selected items
        selected_groups = request.form.getlist("whitelistgroups")
        print(selected_groups)
        for groupid in selected_groups:
            group = WhitelistGroup.query.get(int(groupid))
            print(group)
            db.session.delete(group)

        db.session.commit()


    return render_template('main/whitelistgroups.html',
                            whitelistgroups=WhitelistGroup.query.all(),
                            Roles=Roles,
                            dform=dform,
                            rform=rform,
                            title='Whitelist Groups')

@bp.route('/whitelistgroups/add', methods=['POST'])
@login_required
@admin_required
def add_whitelistgroups():
    rform = WhitelistGroupForm()
    rform.role.choices = [(r.id, r.name) for r in Roles.query.all()]
    if rform.validate_on_submit():
        group = WhitelistGroup(groupname=rform.groupname.data)
        group.role_id = rform.role.data
        db.session.add(group)
        db.session.commit()
        return redirect(url_for('main.whitelistgroups'))
    # in the case of validation errors,
    # use the same page again!
    return render_template('main/whitelistgroups.html',
                            title='Whitelist Groups',
                            groups=WhitelistGroup.query.all(),
                            Roles=Roles,
                            rform=rform,
                            dform=DeleteWhitelistGroupForm())


@bp.route('/adduser', methods=['GET', 'POST'])
@login_required
def add_whitelistuser():
    form = AddUserForm()
    form2 = UploadUserForm()

    if form.validate_on_submit():
        print('Add users')
        # textfield is string
        data = form.users.data.split('\n')
        for i in data:
            print(i)

    return render_template('main/add_user.html',
                            title='Add Whitelist User',
                            form=form,
                            form2=form2)


@bp.route('/uploaduser', methods=['POST'])
@login_required
def upload_whitelistuser():

    # get the file from the request
    f = request.files["file"]

    # split the lines from the submitted file
    for i in f:
        print(i.decode('utf8').strip())

    msg = 'User added'
    res = make_response(jsonify({"message": msg}), 200)

    return res

