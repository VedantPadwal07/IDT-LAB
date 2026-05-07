#!/usr/bin/env bash
# Render Build Script for Fenestra Pro
set -o errexit

# Install Python dependencies
pip install -r requirements.txt

# Navigate to the Django project root
cd fenestra_pro

# Collect static files (CSS, JS, images) for WhiteNoise
python manage.py collectstatic --no-input

# Apply database migrations
python manage.py migrate
