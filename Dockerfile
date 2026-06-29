FROM python:3.12-slim

WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*
COPY . .

RUN pip install --no-cache-dir . && \
    chmod +x /app/scripts/start-sso.sh

HEALTHCHECK --interval=30s --timeout=5s CMD curl -f http://localhost:${API_PORT:-8000}/auth/openapi.json || exit 1

EXPOSE 8000

CMD ["/app/scripts/start-sso.sh"]
