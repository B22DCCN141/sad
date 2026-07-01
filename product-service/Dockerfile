FROM python:3.10-slim
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# Default: migrate + seed + run server
CMD ["sh", "-c", "python manage.py migrate --settings=config.settings.dev && python manage.py seed_categories --settings=config.settings.dev && python manage.py seed_products --settings=config.settings.dev && python manage.py runserver 0.0.0.0:8000 --settings=config.settings.dev"]
