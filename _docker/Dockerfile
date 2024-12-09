FROM python:3.9-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файл зависимостей (requirements.txt) в контейнер
COPY ../requirements.txt .

# Устанавливаем зависимости проекта
RUN pip install --no-cache-dir -r requirements.txt

# # Копируем весь проект в контейнер нужна на этапе выпуска продакшена вместо volumes в docker-compose
# COPY ../backend .

# # Указываем команду для запуска приложения
# CMD ["python", "backend/manage.py", "runserver", "0.0.0.0:8000"]

