#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Convert static asset files
python manage.py collectstatic --no-input

# Apply any outstanding database migrations
python manage.py makemigrations
python manage.py migrate

# Create a superuser non-interactively
# Set default values for username, email, and password (customize as needed)
DJANGO_SUPERUSER_USERNAME=${DJANGO_SUPERUSER_USERNAME:-"admin"}
DJANGO_SUPERUSER_EMAIL=${DJANGO_SUPERUSER_EMAIL:-"admin@example.com"}
DJANGO_SUPERUSER_PASSWORD=${DJANGO_SUPERUSER_PASSWORD:-"admin123"}

echo "Creating Django superuser..."
python manage.py createsuperuser \
  --noinput \
  --username "$DJANGO_SUPERUSER_USERNAME" \
  --email "$DJANGO_SUPERUSER_EMAIL" || true  # Ignore errors if superuser already exists

# Set the superuser password (since --noinput doesn’t prompt for it)
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); user = User.objects.filter(username='$DJANGO_SUPERUSER_USERNAME').first(); user.set_password('$DJANGO_SUPERUSER_PASSWORD') if user else None; user.save() if user else None"

echo "Superuser created with username: $DJANGO_SUPERUSER_USERNAME, email: $DJANGO_SUPERUSER_EMAIL, password: $DJANGO_SUPERUSER_PASSWORD"