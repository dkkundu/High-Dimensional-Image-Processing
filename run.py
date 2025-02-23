import os
from dotenv import load_dotenv
# WSGI Server for Development
# Use this during development vs. apache. Can view via [url]:8001
# Run using virtualenv. 'env/bin/python run.py'
from app import create_app, db  # Import the create_app function and db instance

load_dotenv()  # Load environment variables from .env file
app, db = create_app()  # Initialize the app and db

# Set the FLASK_APP environment variable
os.environ['FLASK_APP'] = 'run.py'

if __name__ == "__main__":
    port = int(os.getenv('PORT', 8001))
    debug = os.getenv('DEBUG', 'True').lower() in ['true', '1', 't', 'y', 'yes']
    app.run(host='0.0.0.0', port=port, debug=debug)