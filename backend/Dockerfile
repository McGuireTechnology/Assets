FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

WORKDIR /app

RUN addgroup --system assets && adduser --system --ingroup assets assets

COPY backend/requirements.txt backend/requirements.txt
RUN python -m pip install --upgrade pip \
    && python -m pip install --no-cache-dir -r backend/requirements.txt

COPY backend backend
COPY VERSION VERSION
RUN mkdir -p .data && chown -R assets:assets /app

USER assets
EXPOSE 8080

CMD ["sh", "-c", "python -m uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port ${PORT:-8080}"]
