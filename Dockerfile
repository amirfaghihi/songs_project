FROM python:3.14-slim AS builder

WORKDIR /app

RUN pip install uv

COPY pyproject.toml ./

RUN uv pip install --system --no-cache-dir -r pyproject.toml

FROM python:3.14-slim

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.14/site-packages /usr/local/lib/python3.14/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY songs_api ./songs_api
COPY wsgi.py ./
COPY songs.json ./

ENV PYTHONUNBUFFERED=1

EXPOSE 5000

CMD ["gunicorn", "wsgi:app", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120"]



