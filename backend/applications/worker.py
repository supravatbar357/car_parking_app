from celery import Celery, Task
from flask import current_app

def make_celery(app):
    class FlaskTask(Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():  # ensures DB access works inside tasks
                return self.run(*args, **kwargs)

    celery_app = Celery(
        app.import_name,
        broker=app.config['CELERY_BROKER_URL'],
        backend=app.config['CELERY_RESULT_BACKEND'],
        include=["applications.task"]  # auto-discover tasks
    )
    celery_app.Task = FlaskTask
    return celery_app
