"""
Auto-create superuser for Render deployment.
Run with: python manage.py shell < create_superuser.py
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fenestra_pro.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@fenestrapro.com')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123')
role = os.environ.get('DJANGO_SUPERUSER_ROLE', 'maker')

if not User.objects.filter(username=username).exists():
    user = User.objects.create_superuser(username=username, email=email, password=password)
    user.role = role
    user.save()
    print(f'Superuser "{username}" created with role "{role}"')
else:
    print(f'Superuser "{username}" already exists')
