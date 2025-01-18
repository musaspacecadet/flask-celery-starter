from flask import Flask

from celery import Celery, Task

from app.models import User, db, migrate
from werkzeug.security import generate_password_hash



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

def create_app(local=False) -> Flask:
    app = Flask(__name__)
    
    # Determine Redis host based on environment
    redis_host = "localhost" if local else "redis"
    redis_url = f"redis://{redis_host}:6379/0"
    
    app.config.from_mapping(
        SECRET_KEY="your_secret_key",  # Add a secret key
        SQLALCHEMY_DATABASE_URI="sqlite:///app.db",
        CELERY=dict(
            broker_url=redis_url,
            result_backend=redis_url,
            task_ignore_result=True,
        ),
    )
    
    # Initialize extensions
    db.init_app(app)
    
    @app.before_first_request
    def create_tables():
        db.create_all()
        # Check if the user already exists
        user = User.query.filter_by(username='admin').first()
        if not user:
            # Hash the password
            hashed_password = generate_password_hash('password')  # Replace with your actual password
            # Create a new user
            new_user = User(
                username='admin',
                email='admin@example.com',
                password_hash=hashed_password,
                verified=True
            )
            db.session.add(new_user)
            db.session.commit()
    
    migrate.init_app(app, db)
    celery_init_app(app)
    
    from .auth import bp as auth_bp
    from .main import bp as main_bp
    from .feed import bp as feeds_bp
    from .auth import login_manager, avatars, mail
    
    login_manager.init_app(app)
    avatars.init_app(app)
    mail.init_app(app)
    
    app.register_blueprint(auth_bp, url_prefix="/challenge")
    app.register_blueprint(feeds_bp, url_prefix="/feeds")
    app.register_blueprint(main_bp)
    
    return app