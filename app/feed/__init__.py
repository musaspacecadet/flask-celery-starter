from flask import Blueprint

bp = Blueprint("feeds", __name__, template_folder="templates")

from . import routes