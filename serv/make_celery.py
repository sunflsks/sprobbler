from web.app import create_app

app = create_app()
celery = app.extensions["celery"]
