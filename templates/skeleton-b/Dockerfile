# B안: standard library only -> one stage, nothing to install
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /srv/backend
COPY backend/app ./app
COPY frontend/index.html /srv/frontend/index.html
COPY frontend/src /srv/frontend/src
COPY data /srv/data
RUN useradd --create-home appuser && mkdir -p /srv/backend/runtime && chown -R appuser /srv
USER appuser
ENV FRONTEND_DIR=/srv/frontend DB_URL=sqlite:////srv/backend/runtime/app.db RUNTIME_DIR=/srv/backend/runtime PORT=3000
EXPOSE 3000
HEALTHCHECK --interval=10s --timeout=3s --start-period=5s CMD python -c "import urllib.request;urllib.request.urlopen('http://127.0.0.1:3000/health',timeout=3)"
CMD ["python", "-m", "app"]
