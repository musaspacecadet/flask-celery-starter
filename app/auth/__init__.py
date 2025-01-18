from flask import Blueprint
from flask_login import LoginManager
from flask_mail import Mail
from flask_avatars import Avatars


bp = Blueprint('auth', __name__, template_folder='templates')
login_manager = LoginManager()
avatars = Avatars()
mail = Mail()

from . import routes


