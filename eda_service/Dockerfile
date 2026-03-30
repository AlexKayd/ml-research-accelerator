FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=180 \
    TZ=UTC \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    PYTHONIOENCODING=utf-8 \
    PYTHONUTF8=1 \
    API_PORT=8003 \
    SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt \
    REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt \
    PIP_CERT=/etc/ssl/certs/ca-certificates.crt


RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ca-certificates \
    libpq-dev \
    libgomp1 \
    curl \
    && update-ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

ARG PYPI_INDEX_URL=https://pypi.org/simple
ARG PIP_TRUSTED_HOSTS=1
RUN set -eux; \
    TRUST=""; \
    if [ "$PIP_TRUSTED_HOSTS" = "1" ]; then \
      TRUST="--trusted-host pypi.org --trusted-host www.pypi.org --trusted-host files.pythonhosted.org --trusted-host pypi.python.org"; \
    fi; \
    python -m pip install --no-cache-dir \
      --index-url "${PYPI_INDEX_URL}" \
      ${TRUST} \
      --default-timeout=180 \
      --retries=8 \
      -r requirements.txt

COPY . .

RUN useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app

USER appuser

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD sh -c 'curl -fsS "http://127.0.0.1:${API_PORT:-8003}/health" || exit 1'

EXPOSE 8003

CMD ["sh", "-c", "exec uvicorn app.cmd.main:app --host 0.0.0.0 --port ${API_PORT:-8003} --workers 1 --loop uvloop --log-level $(echo \"${LOG_LEVEL:-info}\" | tr '[:upper:]' '[:lower:]')"]
