#!/bin/bash
echo "Starting Container"
python -u manage.py migrate
echo "Migrated, starting tests"
pytest -s .
echo "Collected, now starting server"
python -u manage.py runserver 0.0.0.0:8000 --insecure