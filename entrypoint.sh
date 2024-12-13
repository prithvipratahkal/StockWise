#!/bin/sh

# Wait for PostgreSQL to be available
echo "Waiting for PostgreSQL..."

while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
  sleep 0.1
done

echo "PostgreSQL started"

# Run database migrations
python manage.py migrate

# Start the server
exec "$@"
