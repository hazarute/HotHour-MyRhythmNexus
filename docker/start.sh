#!/usr/bin/env sh
set -eu

if [ "${RUN_MIGRATIONS:-true}" = "true" ]; then
  prisma migrate deploy
fi

exec gunicorn \
  -k uvicorn.workers.UvicornWorker \
  app.main:app \
  --bind 0.0.0.0:${PORT:-8000} \
  --workers ${WEB_CONCURRENCY:-2} \
  --timeout ${WEB_TIMEOUT:-120} \
  --forwarded-allow-ips='*'
