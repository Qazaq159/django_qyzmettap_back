#!/bin/sh

ENV_FILE="/app/.env"

echo "Waiting for STRIPE_WEBHOOK_SECRET to appear in .env..."

while [ ! -f "$ENV_FILE" ] || ! grep -q "STRIPE_WEBHOOK_SECRET=whsec_" "$ENV_FILE"; do
  echo "Still waiting for STRIPE_WEBHOOK_SECRET..."
  sleep 2
done

echo "STRIPE_WEBHOOK_SECRET found. Starting Django server..."

python manage.py migrate --noinput
python manage.py collectstatic --noinput
gunicorn qyzmettap_back.wsgi:application \
  --timeout 180 \
  --bind 0.0.0.0:8000 \
  --workers 8 \
  --log-level debug
