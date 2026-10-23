# ========================================================
# Festify — Production Multi-Stage Hardened Dockerfile
# ========================================================
FROM python:3.12-slim AS builder

WORKDIR /build

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --user --no-warn-script-location -r requirements.txt


# ========================================================
# Runtime Stage: Minimal & Non-Root
# ========================================================
FROM python:3.12-slim AS runner

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/home/festifyuser/.local/bin:${PATH}" \
    FESTIFY_ENVIRONMENT=production \
    PORT=8000

# Security: Create non-root system group and user
RUN groupadd -g 10001 festifygroup && \
    useradd -u 10001 -g festifygroup -m -s /bin/sh festifyuser

# Copy installed python dependencies from builder
COPY --from=builder /root/.local /home/festifyuser/.local

# Copy application source code
COPY --chown=festifyuser:festifygroup app/ /app/app/
COPY --chown=festifyuser:festifygroup frontend/ /app/frontend/
COPY --chown=festifyuser:festifygroup index.html /app/index.html
COPY --chown=festifyuser:festifygroup requirements.txt /app/

# Ensure directory permissions
RUN chown -R festifyuser:festifygroup /app /home/festifyuser

USER festifyuser

EXPOSE 8000

# Built-in lightweight health check (does not require curl)
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request, sys; sys.exit(0 if urllib.request.urlopen('http://localhost:' + str(__import__('os').environ.get('PORT', 8000)) + '/api/health').getcode() == 200 else 1)"

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 2"]
