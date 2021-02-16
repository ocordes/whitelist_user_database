"""

app/auth/routes.py

written by: Oliver Cordes 2021-02-13
changed by: Oliver Cordes 2021-02-13

"""

import os
from datetime import datetime

from flask import current_app, request, render_template, \
                  url_for, flash, redirect
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse


from app import db
from app.auth import bp
from app.auth.forms import LoginForm, EditProfileForm, \
                           UpdatePasswordForm, ResetPasswordRequestForm, \
                           ResetPasswordForm, AdminPasswordForm, \
                           PreferencesForm
from app.models import User

from app.auth.admin import admin_required

#from app.utils.files import read_logfile


APP_ROOT = os.path.dirname(os.path.abspath(__file__))


@bp.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    # so at this point we need to check if we have
    # a clean installation, just ask for admin
    # credentials
    if User.query.count()==0:  # no users available
        form = AdminPasswordForm()
        if form.validate_on_submit():
            user = User(username='admin', email='')
            user.set_password(form.password.data)
            user.first_name = 'System'
            user.last_name = 'Administrator'
            user.is_active = True
            user.administrator = True
            db.session.add(user)

            #user = User.query.get(1)
            #user.set_password(form.password.data)

            db.session.commit()

            flash('Password for the administrator account is now set!')
            return redirect(url_for('auth.login'))

        flash('No users in database! Enter an administrator password!')
        return render_template('auth/admin_password.html',
            title='Set Administrator Password', form=form)
    else:
        # proceed with the normal login procedure
        form = LoginForm()

        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user is None or not user.check_password(form.password.data):
                flash('Invalid username or password')
                msg = 'Invalid username or password (username={})'.format(form.username.data)
                current_app.logger.info(msg)
                return redirect(url_for('auth.login'))
            if login_user(user, remember=form.remember_me.data):
                msg = 'User \'{}\' logged in!'.format(user.username)
                current_app.logger.info(msg)
                next_page = request.args.get('next')
                if not next_page or url_parse(next_page).netloc != '':
                    next_page = url_for('main.index')
                return redirect(next_page)
            else:
                msg = 'User account is not active!'
                flash(msg)
                current_app.logger.info(msg)
                return redirect(url_for('auth.login'))
        return render_template('auth/login.html', title='Sign In',
                                form=form,
                                rform=RegistrationForm(),
                                pform=ResetPasswordRequestForm() )


@bp.route('/logout')
def logout():
    username = current_user.username
    logout_user()
    msg = 'User \'{}\' logged out!'.format(username)
    current_app.logger.info(msg)
    return redirect(url_for('main.index'))




@bp.route('/update_password', methods=['POST'])
def update_password():
    pform=UpdatePasswordForm()


    if pform.validate_on_submit():
        current_user.set_password(pform.password.data)
        db.session.commit()
        flash('Your new password has been saved.')

    return redirect(url_for('auth.user', username=current_user.username))
