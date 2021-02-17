"""

app/__init__.py

written by: Oliver Cordes 2021-02-12
changed by: Oliver Cordes 2021-02-17

"""

import os
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler

from config import Config


from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail, email_dispatched
from flask_debugtoolbar import DebugToolbarExtension



db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
login.login_message = 'Please log in to access this page.'
mail = Mail()
bootstrap = Bootstrap()
#moment = Moment()
#babel = Babel()
toolbar = DebugToolbarExtension()



# define the app in the module ;-)


def create_app(config_class=Config):

    app = Flask(__name__)
    #app = connexion.App(__name__, specification_dir='./api/')
    # Read the swagger.yml file to configure the endpoints
    #app.add_api('openapi.yaml')

    # attach the config
    app.config.from_object(Config)

    app.debug = app.config['DEBUG']

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    mail.init_app(app)
    bootstrap.init_app(app)
    #moment.init_app(app.app)
    #babel.init_app(app.app)

    toolbar.init_app(app)

    # register the blueprints
    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)


    # data dir
    if not os.path.exists(app.config['DATA_DIR']):
        os.mkdir(app.config['DATA_DIR'])

    # error handler

    if app.config['MAIL_SERVER']:
        auth = None
        if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
            auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        secure = None
        if app.config['MAIL_USE_TLS']:
            secure = ()
        mail_handler = SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                #fromaddr='no-reply@' + app.config['MAIL_SERVER'],
                fromaddr='ocordes@astro.uni-bonn.de',
                toaddrs=app.config['ADMINS'], subject='Server Failure',
                credentials=auth, secure=secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)


    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/server.log', maxBytes=10240,
                                       backupCount=10)
    file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('Server startup')

    app.config['logfile'] = 'logs/server.log'

    return app


# import the sub modules
from app import models
