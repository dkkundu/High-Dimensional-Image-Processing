#!/bin/bash

# Activate the virtual environment
source venv/bin/activate

# Run Flask migrations
flask db upgrade

# Deactivate the virtual environment
deactivate
