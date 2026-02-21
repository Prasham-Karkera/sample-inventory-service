FROM python:3.12-slim
LABEL service="inventory-service"
RUN groupadd --gid 1001 appgroup && useradd --uid 1001 --gid appgroup --shell /bin/bash --create-home appuser
WORKDIR /app
COPY pyproject.toml ./
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir .
COPY app/ ./app/
USER appuser
EXPOSE 8003
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8003/health/live')"
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8003", "--workers", "2"]
