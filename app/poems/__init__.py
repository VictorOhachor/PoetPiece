from flask import Blueprint

poems = Blueprint('poems', __name__, url_prefix='/poems')

from . import views