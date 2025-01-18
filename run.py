from app import create_app
import multiprocessing
from celery.bin import worker

flask_app = create_app(True)
celery_app = flask_app.extensions["celery"]

def run_celery_worker():
    worker = celery_app.Worker()
    worker.start()

if __name__ == "__main__":
    # Start Celery worker in a separate process
    celery_process = multiprocessing.Process(target=run_celery_worker)
    celery_process.start()
    
    # Run the Flask app
    try:
        flask_app.run(host="0.0.0.0", port=5000, debug=True)
    finally:
        # Ensure the Celery worker is terminated when Flask exits
        celery_process.terminate()
        celery_process.join()