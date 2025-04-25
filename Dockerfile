FROM python:3.13.3-slim-bookworm

WORKDIR /app

RUN groupadd -g 1000 app && useradd -m -u 1000 -g app app

COPY --chown=app . .

RUN mkdir -p /app/logs && \
    chown -R app:app /app/logs && \
    chmod -R 775 /app/logs

RUN mkdir -p /app/data && \
    chown -R app:app /app/data && \
    chmod -R 777 /app/data

RUN apt-get update && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade pip && pip install -r requirements.txt

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 CMD curl --fail http://dashboard_api:8000/api2/healthcheck || exit 1

USER app


ENTRYPOINT ["gunicorn", "--bind", "0.0.0.0:8000", "-w 2", "app:app"]