#!/usr/bin/env bash
set -o errexit

export DJANGO_SETTINGS_MODULE=config.settings.production

pip install --upgrade pip
pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

# Load seed data if fixture exists and database is empty
python manage.py loaddata fixtures/seed.json || echo "Warning: fixture load failed"
