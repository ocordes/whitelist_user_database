# -*- coding: utf-8 -*-
"""

app/main/routes.py
~~~~~~~~~~~~~~~~~~

written by : Oliver Cordes 2021-02-12
changed by : Oliver Cordes 2021-02-24

"""

import os
from datetime import datetime, timedelta
from dateutil.relativedelta import *
import pkg_resources

from flask import current_app, request, render_template, url_for, flash,  \
    redirect, send_from_directory, jsonify, session, make_response
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse, url_unparse

from flask_paginate import Pagination, get_page_parameter

from app import db
from app.main import bp
from app.models import *
from app.main.forms import WhitelistGroupForm, DeleteWhitelistGroupForm, \
    AddUserForm, DeleteWhitelistUserForm

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
    installed_packages = [(d.project_name, d.version)
                          for d in pkg_resources.working_set][::-1]

    server_users = User.query.count()
    server_roles = Roles.query.count()
    whitelist_users = WhitelistUser.query.count()
    whitelist_groups = WhitelistGroup.query.count()
    return render_template('index.html',
                            installed_packages=installed_packages,
                            server_users=server_users,
                            server_roles=server_roles,
                            whitelist_users=whitelist_users,
                            whitelist_groups=whitelist_groups,
                            title='Dashboard'
                            )


@bp.route('/whiteusers', methods=['GET', 'POST'])
@login_required
def show_users():
    # extract the information from the request
    search = False
    q = request.args.get('q')
    if q:
        search = True
    page     = request.args.get(get_page_parameter(), type=int, default=1)
    groupid  = request.args.get('groupid', type=int, default=0)
    

    # get the form
    dform = DeleteWhitelistUserForm()

    # setup the group box
    if current_user.administrator:
        groups = WhitelistGroup.query.all()
        dform.group.choices = [(0, 'All')]
    else:
        # calculate the groups available for a specific role
        role_ids = [r.id for r in current_user.roles]
        groups = WhitelistGroup.query.filter(
            WhitelistGroup.role_id.in_(role_ids)).all()
        dform.group.choices = []
        dform.group.choices = [(0, 'All')]

    # add all other groups
    dform.group.choices += [(g.id, g.groupname) for g in groups]

    if dform.validate_on_submit():
        if dform.remove.data:
            # get a list of selected items
            selected_users = request.form.getlist("whitelistusers")
            for userid in selected_users:
                 user = WhitelistUser.query.get(int(userid))
                #db.session.delete(user)
            #db.session.commit()
            return redirect(url_for('main.show_users'))

        # must be the group select button
        groupid = dform.group.data

        # reset the view to start from the beginning
        page = 1


    # select the previous selected group
    dform.group.data    = groupid

    # calculate the valid groupids
    if groupid == 0:
        groupids = [g.id for g in groups]
    else:
        groupids = [groupid]

    # calculate the number of valid users from WhiteListUserGroups
    max_users = WhiteListUserGroups.query.filter(WhiteListUserGroups.group_id.in_(groupids)).count()

    pagination = Pagination(page=page, total=max_users,
                            css_framework='bootstrap4',
                            href=url_for('main.show_users') +
                            '?page={}&groupid=%d' % groupid,
                            display_msg='(Displaying <b>{start}-{end}</b> of <b>{total}</b> Users)',
                            search=search, record_name='whitelist_users')

    # select only the users from the pagination setup
    #if groupid == 0:   # all groups
    #    users = WhitelistUser.query.paginate(
    #        page, pagination.per_page, error_out=False).items
    #else:
    #    #role_ids = [r.id for r in current_user.roles]
    #    #groups = WhitelistGroup.query.filter(
    #    #    WhitelistGroup.role_id.in_(role_ids)).all()
    #    #group = WhitelistGroup.query.get(id=groupid)
    #    group_ids = [groupid]
    #    usergroups = WhiteListUserGroups.query.filter(WhiteListUserGroups.group_id.in_(group_ids)).paginate(page, pagination.per_page, error_out=False).items
    #    #users = WhitelistUser.query.filter(WhitelistUser.)
    #    usergroupsids = [i.user_id for i in usergroups]
    #    print(usergroupsids)
    #    users = WhitelistUser.query.filter(WhitelistUser.id.in_(usergroupsids))

    # get the userids from the valid users, using the pagination settings
    usergroups = WhiteListUserGroups.query.filter(WhiteListUserGroups.group_id.in_(
        groupids)).paginate(page, pagination.per_page, error_out=False).items
    usergroupsids = [i.user_id for i in usergroups]
    print(usergroupsids)
    users = WhitelistUser.query.filter(WhitelistUser.id.in_(usergroupsids))


    return render_template('main/users.html',
                            whitelistuser=users,
                            dform=dform,
                            pagination=pagination, 
                            groups=groups,
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
        for groupid in selected_groups:
            group = WhitelistGroup.query.get(int(groupid))
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

    if current_user.administrator:
        groups = WhitelistGroup.query.all()
    else:
        # calculate the groups available for a specific role
        role_ids = [r.id for r in current_user.roles]
        groups = WhitelistGroup.query.filter(WhitelistGroup.role_id.in_(role_ids)).all()

    form.group.choices = [(g.id, g.groupname) for g in groups]

    if form.validate_on_submit():
        print('Add users')
        # textfield is string
        data = form.users.data.split('\n')
        # recompile the list of users regarding to the instructions
        new_data = []
        for line in data:
            line = line.strip()
            if line != '':
                s = line.split(',')
                for i in s:
                    new_data.append(i.strip())

        group = WhitelistGroup.query.get(form.group.data)
        for username in new_data:
            whitelist_user = WhitelistUser.query.filter_by(username=username).first()
            if whitelist_user is None:
                whitelist_user = WhitelistUser(username=username)
                whitelist_user.comment = ''
                db.session.add(whitelist_user)
            whitelist_user.roles.append(group)
            db.session.commit()

        return redirect(url_for('main.show_users'))

    return render_template('main/add_user.html',
                            title='Add Whitelist User',
                            form=form,
                            groups=groups)


@bp.route('/uploaduser/<groupid>', methods=['POST'])
@login_required
def upload_whitelistuser(groupid):

    # get the file from the request
    f = request.files["file"]

    # split the lines from the submitted file
    for i in f:
        print(i.decode('utf8').strip())

    print(groupid)

    msg = 'User added'
    res = make_response(jsonify({"message": msg}), 200)

    return res

