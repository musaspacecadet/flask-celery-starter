# musaspacecadet-flask-celery-starter

This repository contains a starter project for a Flask web application with Celery integration for background tasks. It's designed for easy setup and deployment using Docker and Docker Compose.

## Features

-   **Flask Web Application:** A basic Flask app structure with blueprints for modularity.
-   **Celery Integration:** Celery configured to use Redis as a message broker for handling asynchronous tasks.
-   **Dockerized Development:**  Easily run the application and its dependencies (Redis) in isolated containers using Docker Compose.
-   **Supervisor:** Uses Supervisor to manage Flask and Celery worker processes within the Docker container.
-   **User Authentication:** Includes a basic user authentication system with registration, login, password reset, and email verification using Flask-Login, Flask-Mail, and Flask-Avatars.
-   **Database:** Uses SQLAlchemy for database interactions with SQLite as the default database (easily configurable to other database systems).
-   **Database Migrations:**  Flask-Migrate for managing database schema changes.
-   **RSS Feed Handling:** Pre-configured with a list of RSS feed URLs (in `rss.py`). (Note: No active functionality to process these feeds is implemented in the provided code.)
-   **Forms:** Uses WTForms for handling user input and validation.

## Directory Structure

```
musaspacecadet-flask-celery-starter/
├── Dockerfile
├── docker-compose.yml
├── make_celery.py
├── requirements.txt
├── rss.py
├── run.py
├── app/
│   ├── __init__.py
│   ├── forms.py
│   ├── models.py
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── templates/
│   │       ├── login.html
│   │       ├── registration.html
│   │       ├── reset_password.html
│   │       └── reset_password_request.html
│   ├── feed/
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   ├── tasks.py
│   │   └── templates/
│   │       └── feeds/
│   │           └── index.html
│   ├── main/
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── templates/
│   │       └── main/
│   │           └── index.html
│   └── templates/
│       └── base.html
├── instance/
│   └── app.db
└── supervisor/
    └── supervisord.conf
```

## Getting Started

### Prerequisites

-   Docker
-   Docker Compose

### Installation

1. **Clone the repository:**

    ```bash
    git clone <repository_url>
    cd musaspacecadet-flask-celery-starter
    ```

2. **Build and run the Docker containers:**

    ```bash
    docker-compose up --build
    ```

    This command will:

    -   Build the Docker image for the Flask application.
    -   Start a Redis container.
    -   Start the Flask application container, which includes:
        -   The Flask development server running on port 5000.
        -   A Celery worker process.
        -   Supervisor to manage the Flask and Celery processes.

3. **Access the application:**

    Open your web browser and go to `http://localhost:5000`.

## Usage

### User Authentication

-   **Registration:** Navigate to `/challenge/register` to create a new user account.
-   **Login:** Navigate to `/challenge/login` to log in with an existing account.
-   **Password Reset:** Use the "Forgot password" link on the login page to initiate a password reset.
-   **Email Verification:** After registration or password reset, an email will be sent for verification (check your console for the email content in development).

###  (Placeholder) RSS Feed Handling:

-   The `rss.py` file contains a list of RSS feed URLs.
-   The `app/feed` blueprint is set up for potential RSS feed processing functionality (currently, there are no active routes or tasks to process the feeds).

### Extending the Application

-   **Adding new routes:** Create new blueprints or add routes to existing blueprints (e.g., `app/main/routes.py`, `app/feed/routes.py`).
-   **Creating new Celery tasks:** Define tasks in `app/feed/tasks.py` or create new task files and import them into your application.
-   **Database models:** Modify or add new database models in `app/models.py`.
-   **Templates:** Update or create new HTML templates in the `app/templates` directory.

## Configuration

-   **Secret Key:** Change the `SECRET_KEY` in `app/__init__.py` to a strong, unique secret key for production environments.
-   **Database URI:** The default database URI is `sqlite:///app.db`. You can modify `SQLALCHEMY_DATABASE_URI` in `app/__init__.py` to use a different database.
-   **Celery Settings:** Adjust Celery settings (broker URL, result backend) in the `CELERY` configuration dictionary within `app/__init__.py`.
-   **Email Settings:** Configure Flask-Mail settings in `app/__init__.py` to enable sending emails in a production environment.

## Deployment

This project is configured for easy deployment using Docker. You can adapt the `Dockerfile` and `docker-compose.yml` to suit your specific deployment needs. Consider using a production-ready WSGI server like Gunicorn instead of the Flask development server for production deployments.

## Notes

-   This project is a basic starter and may require further development for specific features and production readiness.
-   The RSS feed handling functionality is currently a placeholder and needs to be implemented based on your requirements.
-   Remember to properly configure email settings and change the default secret key for production deployments.
-   The provided  `rss.py`  file lists numerous RSS feed URLs, but there's no code provided to actively fetch, parse, or display content from these feeds. You'll need to add the necessary logic within the  `app/feed`  blueprint (or elsewhere) to implement this functionality. For example, you could create Celery tasks that periodically fetch and parse these feeds, storing the data in the database.
-   The project does not include any specific instructions or functionality related to the name "musaspacecadet". This might be a placeholder or a personal identifier. You can safely rename the repository and adjust the code accordingly if you wish to personalize it further.
