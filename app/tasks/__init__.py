from flask import Blueprint

bp = Blueprint("tasks", __name__, template_folder="templates")

from . import routes