FROM postgres:16-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DRIFT_DB_HOST=127.0.0.1 \
    DRIFT_DB_PORT=5432 \
    DRIFT_DB_NAME=drift_monitoring \
    DRIFT_DB_USER=postgres \
    DRIFT_CHART_SELECTOR_PORT=8765 \
    LLM_INTERPRETATION_SERVER_PORT=8767

RUN apt-get update \
    && apt-get install -y --no-install-recommends python3 python3-pip python3-venv supervisor \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/drift_llm_intepretation

COPY requirements.docker.txt /tmp/requirements.docker.txt
RUN python3 -m pip install --break-system-packages --no-cache-dir -r /tmp/requirements.docker.txt \
    && rm /tmp/requirements.docker.txt

COPY . /opt/drift_llm_intepretation
COPY docker/supervisord.conf /etc/supervisor/conf.d/drift_llm.conf
COPY docker/entrypoint.sh /usr/local/bin/drift-llm-entrypoint.sh
RUN chmod +x /usr/local/bin/drift-llm-entrypoint.sh

EXPOSE 8765 8766 8767 8770 5432

ENTRYPOINT ["/usr/local/bin/drift-llm-entrypoint.sh"]
