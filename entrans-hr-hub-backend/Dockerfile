FROM python:3.11-slim

WORKDIR /app

COPY myproject/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

WORKDIR /app/myproject

# Collect static files
RUN DATABASE_URL=sqlite:///:memory: python manage.py collectstatic --noinput

# Run collectstatic during build (using dummy env vars if needed)
# Cloud Run sets the PORT environment variable
EXPOSE $PORT

# Start gunicorn
CMD exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 0 myproject.wsgi:application