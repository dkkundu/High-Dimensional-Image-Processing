#!/bin/bash
exec gunicorn -b 0.0.0.0:${PORT:-8001} wsgi:app
