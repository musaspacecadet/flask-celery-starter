from flask import render_template
from . import bp
from flask_login import login_required, current_user


@bp.route("/")
@login_required
def index():
    return render_template("main/index.html")