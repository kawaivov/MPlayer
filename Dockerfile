# 1. Базовий образ (Python 3.10 slim - легкий)
FROM python:3.10-slim

# 2. Робоча папка всередині контейнера
WORKDIR /app

# 3. Змінні оточення (щоб Python не буферизував вивід)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 4. Встановлення залежностей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Копіювання коду проєкту
COPY . .

# 6. Створюємо папки для медіа (щоб не було помилок при старті)
RUN mkdir -p static/music static/covers

# 7. Відкриваємо порт (інформативно)
EXPOSE 8080

# 8. Команда запуску (Gunicorn запускає app:app на 0.0.0.0:8080)
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8080", "app:app"]