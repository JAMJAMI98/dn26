# 1) build frontend
FROM node:22-slim AS web
WORKDIR /web
COPY frontend/package*.json ./
RUN npm ci || npm install
COPY frontend/ ./
RUN npm run build

# 2) runtime: backend serves API + built frontend on one port
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /srv/backend
COPY backend/pyproject.toml ./
COPY backend/app ./app
RUN pip install --no-cache-dir .
COPY --from=web /web/dist /srv/frontend/dist
COPY data /srv/data
RUN useradd --create-home appuser && mkdir -p /srv/backend/runtime && chown -R appuser /srv
USER appuser
ENV FRONTEND_DIST=/srv/frontend/dist DB_URL=sqlite:////srv/backend/runtime/app.db RUNTIME_DIR=/srv/backend/runtime PORT=3000
EXPOSE 3000
HEALTHCHECK --interval=10s --timeout=3s --start-period=10s CMD python -c "import urllib.request;urllib.request.urlopen('http://127.0.0.1:3000/health',timeout=3)"
CMD ["python", "-m", "app"]
