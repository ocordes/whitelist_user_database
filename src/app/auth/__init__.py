"""

app/auth/__init__.py

written by: Oliver Cordes 2021-02-13
changed by: Oliver Cordes 2021-02-16

"""


from flask import Blueprint

bp = Blueprint('auth', __name__)

from app.auth import routes, users
