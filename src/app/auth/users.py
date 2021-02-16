"""

app/auth/users.py

written by: Oliver Cordes 2021-02-16
changed by: Oliver Cordes 2021-02-16

"""


from flask import current_app, request, render_template, \
                  url_for, flash, redirect
from flask_login import current_user, login_required

from sqlalchemy import desc

from app import db
from app.auth import bp
from app.models import User, Roles

from app.auth.forms import UserListForm, RolesForm, DeleteRolesForm, \
                            NewUserForm, \
                            EditProfileForm, UpdatePasswordForm


from app.auth.admin import admin_required



@bp.route('/users', methods=['GET','POST'])
@login_required
@admin_required
def users():
    form = UserListForm()
    if form.validate_on_submit():
        # get a list of selected items
        selected_users = request.form.getlist("users")

        for uid in selected_users:
            # skip admin account
            if uid == '1':
                continue
            user = User.query.get(int(uid))
            # sets admin role
            if form.set_admin.data:
                if not user.administrator:
                    msg = 'set admin for user={} ({})'.format(uid,user.username)
                    current_app.logger.info(msg)
                    user.administrator = True
                    flash(msg)
            # clear admin role
            elif form.clear_admin.data:
                if user.administrator:
                    msg = 'clear admin for user={} ({})'.format(uid,user.username)
                    current_app.logger.info(msg)
                    user.administrator = False
                    flash(msg)
            # remove account
            elif form.remove.data:
                db.session.delete(user)
                msg = 'remove account user={} ({})'.format(uid,user.username)
                current_app.logger.info(msg)
                flash(msg)

        db.session.commit()
    return render_template('auth/users.html',
                            title='Users',
                            users=User.query.all(), form=form)


@bp.route('/user/<username>', methods=['GET','POST'])
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()

    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('auth.user', username=current_user.username))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.email.data = current_user.email

    return render_template('auth/user.html',
                            title='User preferences',
                            user=user,
                            form=form,
                            projects=user.projects.all(),
                            pform=UpdatePasswordForm())


@bp.route('/newuser', methods=['GET','POST'])
@login_required
@admin_required
def newuser():
    nform = NewUserForm()
    if nform.validate_on_submit():
        selected_roles = request.form.getlist("roles")

        user = User(username=nform.username.data)
        user.set_password(nform.password.data)
        user.first_name = nform.first_name.data
        user.last_name = nform.last_name.data
        user.email = nform.email.data
        user.is_active = True

        # add roles selected from the form
        for roleid in selected_roles:
            user.roles.append(Roles.query.get(int(roleid)))

        db.session.add(user)
        db.session.commit()

        return redirect(url_for('auth.users'))

    return render_template('auth/newuser.html',
                            title='New User',
                            roles=Roles.query.all(),
                            nform=nform)


@bp.route('/roles', methods=['GET', 'POST'])
@login_required
@admin_required
def roles():
    dform = DeleteRolesForm()
    if dform.validate_on_submit():
        # get a list of selected items
        selected_roles = request.form.getlist("roles")

        for roleid in selected_roles:
            role = Roles.query.get(int(roleid))
            db.session.delete(role)

        db.session.commit()

        return redirect(url_for('auth.roles'))

    return render_template('auth/roles.html',
                            title='User roles',
                            roles=Roles.query.all(),
                            rform=RolesForm(),
                            dform=dform)


@bp.route('/roles/add', methods=['POST'])
@login_required
@admin_required
def add_roles():
    rform = RolesForm()
    if rform.validate_on_submit():
        role = Roles(name=rform.rolename.data)
        db.session.add(role)
        db.session.commit()
        return redirect(url_for('auth.roles'))

    # in the case of validation errors,
    # use the same page again!
    return render_template('auth/roles.html',
                            title='User roles',
                            roles=Roles.query.all(),
                            rform=rform,
                            dform=DeleteRolesForm())
