#!/bin/bash

# Set the Flask application
export FLASK_APP=run.py

# Initialize the database (only needed for the first time)
flask db init

# Create a new migration
flask db migrate -m "Initial migration"

# Apply the migration
flask db upgrade

# To create and apply new migrations in the future, use:
# flask db migrate -m "Description of changes"
# flask db upgrade

# Note: Ensure 'app.run()' is only called within an 'if __name__ == "__main__"' guard in your Flask app.
