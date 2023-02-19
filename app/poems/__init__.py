from flask import Blueprint

poems = Blueprint('poems', __name__)

from . import views, errors