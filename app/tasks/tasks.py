from celery import shared_task
from ..models import User
from .. import db

@shared_task(ignore_result=False)
def add_together(a: int, b: int) -> int:
    """Example task that adds two numbers."""
    return a + b

# Example task that processes data for a given user (simulated)
@shared_task
def generate_user_archive(user_id: int) -> None:
    """Simulates generating an archive for a user."""
    print(f"Generating archive for user {user_id}...")
    # Fetch the user from the database
    user = User.query.get(user_id)

    if user:
        print(f"Found user: {user.username}")
        # ... your archive generation code ...
        print(f"Archive for user {user_id} generated.")
    else:
        print(f"User with ID {user_id} not found.")