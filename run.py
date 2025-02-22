import os
from dotenv import load_dotenv
# WSGI Server for Development
# Use this during development vs. apache. Can view via [url]:8001
# Run using virtualenv. 'env/bin/python run.py'
from app import create_app  # Import the create_app function

# Ensure media folder exists
os.makedirs("media/uploads/original", exist_ok=True)
os.makedirs("media/uploads/slice", exist_ok=True)

load_dotenv()  # Load environment variables from .env file
app, db = create_app()  # Initialize the app and get the db instance

port = int(os.getenv('PORT', 8001))
debug = os.getenv('DEBUG', 'True').lower() in ['true', '1', 't', 'y', 'yes']

app.run(host='0.0.0.0', port=port, debug=debug)