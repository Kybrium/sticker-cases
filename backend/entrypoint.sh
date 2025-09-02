#!/usr/bin/env bash
set -e

# Wait a moment just in case
sleep 1

echo "[entrypoint] Applying migrations..."
python manage.py migrate --noinput

# Create superuser only if it doesn't exist
echo "[entrypoint] Ensuring superuser exists..."
python manage.py shell <<'PYCODE'
import os
from django.contrib.auth import get_user_model

User = get_user_model()
username = os.environ.get("DJANGO_SUPERUSER_USERNAME", "admin")
email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "admin@example.com")
password = os.environ.get("DJANGO_SUPERUSER_PASSWORD", "admin")

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f"[entrypoint] Created superuser: {username} / {email}")
else:
    print(f"[entrypoint] Superuser already exists: {username}")
PYCODE

echo "[entrypoint] Starting dev server..."
exec python manage.py runserver 0.0.0.0:8000