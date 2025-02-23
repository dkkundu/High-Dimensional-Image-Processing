import os
import logging
from flask import Flask, render_template, send_from_directory
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from app.admin import setup_admin
from app.routes import register_routes
from app.celery_app import celery, make_celery
from app.tasks import example_task
from app.models import init_db  # Import the init_db function

# Define the SQLAlchemy and Migrate instances globally
db = SQLAlchemy()
migrate = Migrate()

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

    # Initialize SQLAlchemy and Migrate
    db.init_app(app)
    migrate.init_app(app, db)

    # Initialize the database (create tables)
    with app.app_context():
        init_db()

    setup_admin(app)
    register_routes(app)

    celery = make_celery(app)

    # Configure logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Add file handler to save logs to a file
    file_handler = logging.FileHandler('logs/app.log')
    file_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # HTTP error handling
    @app.errorhandler(404)
    def not_found(error):
        logger.error(f"404 error: {error}")
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"500 error: {error}")
        return render_template('500.html'), 500

    @app.route('/')
    def home():
        return render_template('home.html')
    
    @app.route('/media/<path:filename>')
    def media_files(filename):
        return send_from_directory(app.config['MEDIA_ROOT'], filename)

    return app, db