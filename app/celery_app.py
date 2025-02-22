import os
from dotenv import load_dotenv
from celery import Celery

load_dotenv()  # Load environment variables from .env file

broker = os.getenv('CELERY_BROKER_URL')
backend = os.getenv('CELERY_BACKEND_URL')
celery = Celery('app', broker=broker, backend=backend)

# ...additional Celery configuration...

def make_celery(app):
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery