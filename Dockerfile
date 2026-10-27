FROM python:3.13-alpine

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HOST=0.0.0.0 \
    PORT=8000

RUN apk upgrade --no-cache \
    && addgroup -S -g 10001 appuser \
    && adduser -S -D -H -u 10001 -G appuser appuser

COPY --chown=appuser:appuser app/ ./app/

USER appuser

EXPOSE 8000

CMD ["python", "app/main.py"]