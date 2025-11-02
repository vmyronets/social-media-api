FROM python:3.12-alpine

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

COPY . .

RUN mkdir -p /app/media && \
    adduser --disabled-password --no-create-home app_user && \
    chown -R app_user:app_user /app/media && \
    chmod -R 755 /app/media

USER app_user
