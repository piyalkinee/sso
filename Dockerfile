FROM python:3.13-slim

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir . && \
    chmod +x /app/scripts/start-sso.sh

HEALTHCHECK --interval=30s --timeout=5s CMD curl -f http://localhost:${API_PORT:-9897}/health || exit 1

EXPOSE 9897

CMD ["/app/scripts/start-sso.sh"]

