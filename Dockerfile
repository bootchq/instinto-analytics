# Используем образ с Playwright
FROM mcr.microsoft.com/playwright/python:v1.49.1-noble

WORKDIR /app

# Копируем requirements и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Устанавливаем браузеры Playwright
RUN playwright install chromium

# Копируем код
COPY . .

# Запускаем основной скрипт
CMD ["python", "run_railway.py"]
