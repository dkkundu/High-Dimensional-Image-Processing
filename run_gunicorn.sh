#!/bin/bash

source env/bin/activate
exec gunicorn -b 0.0.0.0:${PORT:-8001} app:app
