#!/usr/bin/env bash
set -Eeuo pipefail

if [[ "${POSTGRES_DB:-drift_monitoring}" != "drift_monitoring" ]]; then
  echo "POSTGRES_DB is '${POSTGRES_DB}', while the application expects 'drift_monitoring'." >&2
  echo "Set POSTGRES_DB=drift_monitoring or create that database before starting the web services." >&2
fi

exec /usr/bin/supervisord -n -c /etc/supervisor/conf.d/drift_llm.conf
