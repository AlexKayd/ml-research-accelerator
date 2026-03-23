FROM python:3.11-slim

ENV TZ=Europe/Moscow \
    PIP_DEFAULT_TIMEOUT=180 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir --default-timeout=180 --retries=15 -r requirements.txt

COPY . .

EXPOSE 8001

# потом убрать --reload
CMD ["uvicorn", "app.cmd.main:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]