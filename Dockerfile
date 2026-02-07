FROM python:3.12-slim

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir . && \
    chmod +x /app/scripts/start-sso.sh

HEALTHCHECK --interval=30s --timeout=5s CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

CMD ["/app/scripts/start-sso.sh"]

