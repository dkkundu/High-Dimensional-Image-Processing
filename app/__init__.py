import os
from flask import Flask, render_template, send_from_directory
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from app.admin import setup_admin
from app.routes import register_routes
from app.celery_app import celery, make_celery
from app.tasks import example_task

def create_app():
    app = Flask(__name__, static_folder='static', static_url_path='/static')

    MEDIA_ROOT = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../media')
    MEDIA_URL = '/media/'

    # Ensure the media folder exists
    if not os.path.exists(MEDIA_ROOT):
        os.makedirs(MEDIA_ROOT)

    app.config['MEDIA_ROOT'] = MEDIA_ROOT
    app.config['MEDIA_URL'] = MEDIA_URL

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
    
    @app.route('/media/<path:filename>')
    def media_files(filename):
        return send_from_directory(app.config['MEDIA_ROOT'], filename)

    return app, db