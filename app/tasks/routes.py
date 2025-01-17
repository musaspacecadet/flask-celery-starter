from flask import render_template, request, jsonify, redirect, url_for
from celery.result import AsyncResult
from . import bp
from .. import db
from ..models import User
from .tasks import add_together, generate_user_archive

@bp.route('/add', methods=['GET', 'POST'])
def add_task_form():
    if request.method == 'POST':
        a = request.form.get("a", type=int)
        b = request.form.get("b", type=int)
        result = add_together.delay(a, b)
        return redirect(url_for("tasks.task_result", task_id=result.id))
    return render_template('tasks/add_task_form.html')

@bp.route("/result/<task_id>")
def task_result(task_id):
    """Checks the status and result of a task."""
    result = AsyncResult(task_id)
    return render_template('tasks/task_result.html', result=result)

@bp.route("/generate_archive/<int:user_id>", methods=["POST"])
def start_generate_archive(user_id):
    """Starts the generate_user_archive task."""
    # In a real app, you would check if the user exists, etc.
    result = generate_user_archive.delay(user_id)
    return jsonify({"result_id": result.id})

@bp.route("/add_user", methods=["POST"])
def add_user():
    """Adds a user to the database (example)."""
    username = request.form.get("username")
    if username:
        user = User(username=username)
        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "User added", "user_id": user.id})
    return jsonify({"message": "Username is required"}), 400