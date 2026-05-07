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

# Create superuser automatically from environment variables
python manage.py shell -c "
from django.contrib.auth import get_user_model
import os
User = get_user_model()
username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@fenestrapro.com')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123')
role = os.environ.get('DJANGO_SUPERUSER_ROLE', 'maker')
if not User.objects.filter(username=username).exists():
    user = User.objects.create_superuser(username=username, email=email, password=password)
    user.role = role
    user.save()
    print(f'Superuser {username} created with role {role}')
else:
    print(f'Superuser {username} already exists')
"
