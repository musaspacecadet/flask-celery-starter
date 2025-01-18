from flask import render_template, request, jsonify, redirect, url_for
from celery.result import AsyncResult
from . import bp
from ..models import User, db
#from .tasks import add_together, generate_user_archive


