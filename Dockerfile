# Установка базового образа
FROM python:3.12.0-alpine

# Установка рабочего каталога
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Обновим pip и установим зависимости
RUN pip install --upgrade pip 
COPY ./requirements.txt /app
RUN pip install -r requirements.txt

# Копируем исходный код проекта
COPY . /app

# Предоставляем порт другим приложениям
EXPOSE 8000

# Запуск сервера
CMD ["python", "API_Stripe/manage.py", "runserver", "0.0.0.0:8000"]