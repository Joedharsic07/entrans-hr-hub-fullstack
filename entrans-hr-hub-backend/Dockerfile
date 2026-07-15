FROM python:3.11-slim

WORKDIR /app

COPY requirements/base.txt requirements/production.txt ./requirements/
RUN pip install --no-cache-dir -r requirements/production.txt -r requirements/base.txt

COPY . .

# Collect static files
RUN DATABASE_URL=sqlite:///:memory: python manage.py collectstatic --noinput

# Run collectstatic during build (using dummy env vars if needed)
# Cloud Run sets the PORT environment variable
EXPOSE $PORT

CMD exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 0 config.wsgi:application