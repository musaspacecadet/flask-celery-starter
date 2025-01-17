from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from celery import Celery, Task

# Database
db = SQLAlchemy()
migrate = Migrate()

def celery_init_app(app: Flask) -> Celery:
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_app.config_from_object(app.config["CELERY"])
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    return celery_app

def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY="your_secret_key", # Add a secret key
        SQLALCHEMY_DATABASE_URI="sqlite:///app.db",
        CELERY=dict(
            broker_url="redis://redis:6379/0",
            result_backend="redis://redis:6379/0",
            task_ignore_result=True,
        ),
    )

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    celery_init_app(app)

    # Register blueprints
    from .main import bp as main_bp
    app.register_blueprint(main_bp)

    from .tasks import bp as tasks_bp
    app.register_blueprint(tasks_bp, url_prefix="/tasks")

    return app