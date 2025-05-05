#!/bin/sh

ENV_FILE="/app/.env"

echo "Waiting for STRIPE_WEBHOOK_SECRET to appear in .env..."

while [ ! -f "$ENV_FILE" ] || ! grep -q "STRIPE_WEBHOOK_SECRET=whsec_" "$ENV_FILE"; do
  echo "Still waiting for STRIPE_WEBHOOK_SECRET..."
  sleep 2
done

echo "STRIPE_WEBHOOK_SECRET found. Starting Django server..."

python manage.py migrate
exec python manage.py runserver 0.0.0.0:8000
