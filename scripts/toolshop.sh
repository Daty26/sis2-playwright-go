#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
export TOOLSHOP_SOURCE="${TOOLSHOP_SOURCE:-$PWD/.ci/toolshop}"
export TOOLSHOP_UI_PORT="${TOOLSHOP_UI_PORT:-4201}"
export TOOLSHOP_API_PORT="${TOOLSHOP_API_PORT:-8092}"
compose=(docker compose -p sis2-ci -f ci/compose.yml)

case "${1:-up}" in
  up)
    # Only use a disposable checkout. Never overwrite an existing developer app.
    if [[ "$TOOLSHOP_SOURCE" != "$PWD/.ci/toolshop" ]]; then
      echo 'TOOLSHOP_SOURCE must point to this repository’s .ci/toolshop checkout.' >&2
      exit 1
    fi
    if [[ ! -f "$TOOLSHOP_SOURCE/sprint5/API/.env.example" ]]; then
      echo 'First check out the revision in ci/toolshop-revision.txt into .ci/toolshop.' >&2
      exit 1
    fi
    cp "$TOOLSHOP_SOURCE/sprint5/API/.env.example" "$TOOLSHOP_SOURCE/sprint5/API/.env"
    # The frontend runs in the browser, so it needs the host API port.
    python3 - <<'PY'
import os
from pathlib import Path
path = Path(os.environ['TOOLSHOP_SOURCE']) / 'sprint5/UI/src/environments/environment.ts'
text = path.read_text()
import re
text = re.sub(r"apiUrl: '[^']+'", "apiUrl: 'http://localhost:" + os.environ['TOOLSHOP_API_PORT'] + "'", text)
path.write_text(text)
PY
    "${compose[@]}" up -d --wait mariadb
    "${compose[@]}" up -d laravel-api web angular-ui
    "${compose[@]}" exec -T -u root laravel-api sh -ec '
      COMPOSER_MAX_PARALLEL_PROCESSES=1 composer install --no-dev --prefer-dist --no-interaction --optimize-autoloader --ignore-platform-req=ext-ffi
      chown -R www-data:www-data storage bootstrap/cache
      chmod -R ug+rwX storage bootstrap/cache
      php artisan key:generate --force
      php artisan jwt:secret --force
      # This database belongs only to the disposable sis2-ci project.
      php artisan migrate:fresh --seed --force
    '
    # Probe application responses instead of assuming a fixed startup delay.
    for endpoint in "http://localhost:$TOOLSHOP_API_PORT/status" "http://localhost:$TOOLSHOP_API_PORT/products" "http://localhost:$TOOLSHOP_UI_PORT"; do
      ready=false
      for ((attempt=1; attempt<=120; attempt++)); do
        if curl --fail --silent --max-time 5 "$endpoint" -o /dev/null; then
          ready=true
          break
        fi
        sleep 5
      done
      if [[ "$ready" != true ]]; then
        "${compose[@]}" logs --no-color
        echo "Application did not become ready: $endpoint" >&2
        exit 1
      fi
    done
    echo "Toolshop ready. Run tests with BASE_URL=http://localhost:$TOOLSHOP_UI_PORT"
    ;;
  logs) "${compose[@]}" logs --no-color ;;
  down) "${compose[@]}" down --volumes --remove-orphans ;;
  *) echo "Usage: bash scripts/toolshop.sh {up|logs|down}" >&2; exit 2 ;;
esac
