FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8001

# потом убрать --reload
CMD ["uvicorn", "app.cmd.main:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]