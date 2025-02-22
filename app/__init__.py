import os
from flask import Flask, render_template
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from app.admin import setup_admin
from app.routes import register_routes
from app.celery_app import celery, make_celery
from app.tasks import example_task

def create_app():
    app = Flask(__name__, static_folder='media', static_url_path='/media')
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'media')
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    # Configurations
    app.config.from_object('config.Config')

    # sql alchemy and Migrate instances
    db = SQLAlchemy(app)
    migrate = Migrate(app, db)
    setup_admin(app)
    register_routes(app)

    celery = make_celery(app)

    # HTTP error handling
    @app.errorhandler(404)
    def not_found(error):
        return render_template('404.html'), 404

    @app.route('/')
    def home():
        return render_template('home.html')

    return app, db