#!/bin/sh

echo "Starting stripe listen..."

stripe listen \
  --forward-to web:8000/api/payments/webhook/ \
  --api-key "$STRIPE_SECRET_KEY" \
  --print-secret > /tmp/webhook_secret.txt &

# Подождать генерацию webhook секрета
sleep 3

# Извлечь webhook secret
WEBHOOK_SECRET=$(grep -o 'whsec_[a-zA-Z0-9]*' /tmp/webhook_secret.txt | head -1)

echo "Extracted webhook secret: $WEBHOOK_SECRET"

# Перезаписать переменную в /app/.env
sed -i '/^STRIPE_WEBHOOK_SECRET=/d' /app/.env
echo "STRIPE_WEBHOOK_SECRET=$WEBHOOK_SECRET" >> /app/.env

# Дождаться запуска web (он зависит от stripe)
echo "Waiting for web to boot..."
sleep 10

# Всё готово — оставляем только stripe listen запущенным в foreground
exec stripe listen \
  --forward-to web:8000/api/payments/webhook/ \
  --api-key "$STRIPE_SECRET_KEY"
