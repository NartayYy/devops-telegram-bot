FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл зависимостей
COPY requirements.txt .

# Настраиваем pip для обхода SSL и устанавливаем зависимости
RUN pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --no-cache-dir -r requirements.txt

# Копируем исходный код
COPY src/ .

# Создаем пользователя для безопасности
RUN useradd -m -u 1000 botuser && chown -R botuser /app
USER botuser

# Настраиваем переменные окружения для Python SSL
ENV PYTHONHTTPSVERIFY=0
ENV CURL_CA_BUNDLE=""
ENV REQUESTS_CA_BUNDLE=""

# Запускаем бота
CMD ["python", "bot.py"]



















