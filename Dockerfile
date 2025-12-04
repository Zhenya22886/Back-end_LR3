FROM python:3.11-slim-bullseye

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Render та docker-compose будуть передавати порт через змінну PORT
CMD flask --app app run -h 0.0.0.0 -p $PORT